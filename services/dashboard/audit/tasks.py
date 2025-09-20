"""
Celery tasks for audit app.
"""
from celery import shared_task
from django.utils import timezone
import structlog

logger = structlog.get_logger(__name__)


@shared_task
def cleanup_old_audit_logs():
    """
    Clean up old audit logs to maintain database performance.
    """
    try:
        from .models import AuditLog
        
        # Delete audit logs older than 2 years
        cutoff_date = timezone.now() - timezone.timedelta(days=730)
        deleted_count = AuditLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(
            "cleanup_old_audit_logs_completed",
            deleted_count=deleted_count
        )
        
        return f"Deleted {deleted_count} old audit logs"
    except Exception as e:
        logger.error(
            "cleanup_old_audit_logs_failed",
            error=str(e)
        )
        raise


@shared_task
def create_audit_log(instructor_id, action, resource_type, resource_id=None, 
                    resource_name=None, description="", ip_address=None, 
                    user_agent=None, changes=None, metadata=None):
    """
    Create an audit log entry.
    """
    try:
        from .models import AuditLog
        from instructors.models import Instructor
        instructor = None
        if instructor_id:
            try:
                instructor = Instructor.objects.get(id=instructor_id)
            except Instructor.DoesNotExist:
                pass
        
        audit_log = AuditLog.objects.create(
            instructor=instructor,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            resource_name=resource_name,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes or {},
            metadata=metadata or {}
        )
        
        logger.info(
            "audit_log_created",
            audit_log_id=str(audit_log.id),
            instructor_id=str(instructor_id) if instructor_id else None,
            action=action,
            resource_type=resource_type
        )
        
        return f"Audit log created: {audit_log.id}"
    except Exception as e:
        logger.error(
            "audit_log_creation_failed",
            instructor_id=str(instructor_id) if instructor_id else None,
            action=action,
            resource_type=resource_type,
            error=str(e)
        )
        raise