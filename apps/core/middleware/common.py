"""
Enhanced middleware for comprehensive logging and user activity tracking.
"""
import json
import time
import uuid
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
import structlog

logger = structlog.get_logger("jiroshi").bind(
    module=__name__
)


class APILoggingMiddleware(MiddlewareMixin):
    """
    Comprehensive middleware to log all API calls to ELK stack.
    """
    
    def process_request(self, request):
        """
        Log incoming request details and start timer.
        """
        request.start_time = time.time()
        request.request_id = str(uuid.uuid4())
        
        # Extract request data
        request_data = {
            'request_id': request.request_id,
            'timestamp': timezone.now().isoformat(),
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'remote_addr': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referer': request.META.get('HTTP_REFERER', ''),
            'content_type': request.META.get('CONTENT_TYPE', ''),
            'content_length': request.META.get('CONTENT_LENGTH', 0),
            'x_forwarded_for': request.META.get('HTTP_X_FORWARDED_FOR', ''),
            'host': request.META.get('HTTP_HOST', ''),
            'is_secure': request.is_secure(),
            'is_ajax': request.headers.get('X-Requested-With') == 'XMLHttpRequest',
        }
        
        # Add user information if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            request_data.update({
                'user_id': str(request.user.id),
                'username': request.user.username,
                'user_email': request.user.email,
                'user_roles': getattr(request.user, 'role_names', []),
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser,
            })
        
        # Log request body for POST/PUT/PATCH (excluding sensitive data)
        if request.method in ['POST', 'PUT', 'PATCH'] and request.content_type == 'application/json':
            try:
                body = json.loads(request.body.decode('utf-8'))
                # Remove sensitive fields
                sanitized_body = self.sanitize_request_data(body)
                request_data['request_body'] = sanitized_body
            except (json.JSONDecodeError, UnicodeDecodeError):
                request_data['request_body'] = 'Unable to parse JSON'
        
        # Log to ELK stack
        logger.info(
            "api_request_started",
            **request_data,
            log_type="api_request",
            environment=getattr(request, 'environment', 'unknown')
        )
        
        # Store request data for response logging
        request._logging_data = request_data
    
    def process_response(self, request, response):
        """
        Log response details and calculate performance metrics.
        """
        if not hasattr(request, 'start_time'):
            return response
        
        duration = time.time() - request.start_time
        request_data = getattr(request, '_logging_data', {})
        
        # Response data
        response_data = {
            'request_id': request_data.get('request_id', ''),
            'timestamp': timezone.now().isoformat(),
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'response_size': len(response.content) if hasattr(response, 'content') else 0,
            'content_type': response.get('Content-Type', ''),
        }
        
        # Add response body for errors or if needed
        if response.status_code >= 400:
            try:
                if hasattr(response, 'content'):
                    response_content = response.content.decode('utf-8')
                    if response_content:
                        response_data['response_body'] = json.loads(response_content)
            except (json.JSONDecodeError, UnicodeDecodeError):
                response_data['response_body'] = 'Unable to parse response'
        
        # Performance categorization
        performance_category = self.categorize_performance(duration)
        response_data['performance_category'] = performance_category
        
        # Log to ELK stack
        logger.info(
            "api_request_completed",
            **{**request_data, **response_data},
            log_type="api_response",
            environment=getattr(request, 'environment', 'unknown')
        )
        
        # Track user activity if authenticated
        # if hasattr(request, 'user') and request.user.is_authenticated:
        #     self.track_user_activity(request, response, duration)
        
        return response
    
    def process_exception(self, request, exception):
        """
        Log exceptions with full context.
        """
        request_data = getattr(request, '_logging_data', {})
        duration = time.time() - getattr(request, 'start_time', time.time()) if hasattr(request, 'start_time') else 0
        
        exception_data = {
            'request_id': request_data.get('request_id', ''),
            'timestamp': timezone.now().isoformat(),
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'exception_module': exception.__class__.__module__,
            'duration_ms': round(duration * 1000, 2),
            'stack_trace': self.get_stack_trace(exception),
        }
        
        # Log exception to ELK stack
        logger.error(
            "api_request_exception",
            **{**request_data, **exception_data},
            log_type="api_exception",
            environment=getattr(request, 'environment', 'unknown')
        )
        
        return None
    
    # def track_user_activity(self, request, response, duration):
    #     """
    #     Track user activity for analytics and security.
    #     """
    #     try:
    #         from apps.dashboard.instructors.models import InstructorSession
    #         from audit.tasks import create_audit_log
            
    #         # Track session activity
    #         raw_token = None
    #         auth_header = request.META.get("HTTP_AUTHORIZATION", None)
    #         if auth_header and auth_header.startswith("Bearer "):
    #             raw_token = auth_header.split(" ")[1]

    #         # session_key = raw_token
    #         session_key = None
    #         if session_key:
    #             InstructorSession.objects.update_or_create(
    #                 session_key=session_key,
    #                 defaults={
    #                     'instructor': request.user,
    #                     'ip_address': self.get_client_ip(request),
    #                     'user_agent': request.META.get('HTTP_USER_AGENT', ''),
    #                     'is_active': True,
    #                     'last_activity': timezone.now(),
    #                 }
    #             )
            
    #         # Create audit log for significant actions
    #         if self.should_audit_action(request, response):
    #             create_audit_log.delay(
    #                 instructor_id=str(request.user.id),
    #                 action=self.determine_action(request),
    #                 resource_type=self.determine_resource_type(request),
    #                 resource_id=self.extract_resource_id(request),
    #                 description=f"{request.method} {request.path}",
    #                 ip_address=self.get_client_ip(request),
    #                 user_agent=request.META.get('HTTP_USER_AGENT', ''),
    #                 metadata={
    #                     'status_code': response.status_code,
    #                     'duration_ms': round(duration * 1000, 2),
    #                     'request_id': getattr(request, 'request_id', ''),
    #                 }
    #             )
            
    #         # Log user activity to ELK
    #         logger.info(
    #             "user_activity",
    #             instructor=str(request.user.id),
    #             username=request.user.username,
    #             action=self.determine_action(request),
    #             resource=self.determine_resource_type(request),
    #             ip_address=self.get_client_ip(request),
    #             session_key=session_key,
    #             duration_ms=round(duration * 1000, 2),
    #             timestamp=timezone.now().isoformat(),
    #             log_type="user_activity"
    #         )
            
    #     except Exception as e:
    #         logger.error(
    #             "user_activity_tracking_failed",
    #             error=str(e),
    #             instructor_id=str(request.user.id) if hasattr(request, 'user') else None,
    #             log_type="error"
    #         )
    
    def should_audit_action(self, request, response):
        """
        Determine if the action should be audited.
        """
        # Audit all write operations
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return True
        
        # Audit sensitive GET operations
        sensitive_paths = ['/api/v1/auth/', '/api/v1/audit/', '/admin/']
        if any(request.path.startswith(path) for path in sensitive_paths):
            return True
        
        # Audit failed requests
        if response.status_code >= 400:
            return True
        
        return False
    
    def determine_action(self, request):
        """
        Determine the action type based on request.
        """
        if request.method == 'GET':
            return 'view'
        elif request.method == 'POST':
            return 'create'
        elif request.method in ['PUT', 'PATCH']:
            return 'update'
        elif request.method == 'DELETE':
            return 'delete'
        else:
            return 'unknown'
    
    def determine_resource_type(self, request):
        """
        Extract resource type from request path.
        """
        path_parts = request.path.strip('/').split('/')
        if len(path_parts) >= 3 and path_parts[0] == 'api':
            return path_parts[2]  # e.g., /api/v1/users/ -> users
        return 'unknown'
    
    def extract_resource_id(self, request):
        """
        Extract resource ID from request path.
        """
        path_parts = request.path.strip('/').split('/')
        if len(path_parts) >= 4:
            potential_id = path_parts[3]
            # Check if it looks like a UUID or ID
            if len(potential_id) > 10:  # Likely an ID
                return potential_id
        return None
    
    @staticmethod
    def get_client_ip(request):
        """
        Get the client's IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def sanitize_request_data(data):
        """
        Remove sensitive information from request data.
        """
        sensitive_fields = ['password', 'token', 'secret', 'key', 'authorization']
        
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(field in key.lower() for field in sensitive_fields):
                    sanitized[key] = '[REDACTED]'
                elif isinstance(value, (dict, list)):
                    sanitized[key] = APILoggingMiddleware.sanitize_request_data(value)
                else:
                    sanitized[key] = value
            return sanitized
        elif isinstance(data, list):
            return [APILoggingMiddleware.sanitize_request_data(item) for item in data]
        else:
            return data
    
    @staticmethod
    def categorize_performance(duration):
        """
        Categorize request performance.
        """
        if duration < 0.1:  # < 100ms
            return 'fast'
        elif duration < 0.5:  # < 500ms
            return 'normal'
        elif duration < 2.0:  # < 2s
            return 'slow'
        else:
            return 'very_slow'
    
    @staticmethod
    def get_stack_trace(exception):
        """
        Get formatted stack trace from exception.
        """
        import traceback
        return traceback.format_exc()


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to responses with logging.
    """
    
    def process_response(self, request, response):
        """
        Add security headers to the response and log security events.
        """
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' wss: ws:;"
        )
        
        # Other security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Log security header application
        logger.info(
            "security_headers_applied",
            request_id=getattr(request, 'request_id', ''),
            path=request.path,
            log_type="security"
        )
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware with comprehensive logging.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Check rate limits and log attempts.
        """
        client_ip = APILoggingMiddleware.get_client_ip(request)
        
        # Skip rate limiting for authenticated API requests for now
        if request.path.startswith('/api/') and hasattr(request, 'user') and request.user.is_authenticated:
            return None
        
        # Check rate limit (simplified - in production use Redis with sliding window)
        cache_key = f"rate_limit:{client_ip}:{request.path}"
        current_requests = cache.get(cache_key, 0)
        
        # Log rate limit check
        logger.info(
            "rate_limit_check",
            client_ip=client_ip,
            path=request.path,
            method=request.method,
            current_requests=current_requests,
            log_type="rate_limit"
        )
        
        # Simple rate limiting (100 requests per minute per IP per endpoint)
        if current_requests >= 100:
            logger.warning(
                "rate_limit_exceeded",
                client_ip=client_ip,
                path=request.path,
                method=request.method,
                requests_count=current_requests,
                log_type="security_violation"
            )
            
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.'
            }, status=429)
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, 60)  # 1 minute window
        
        return None