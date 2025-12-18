# Headless LMS CORS Configuration

This document details the Cross-Origin Resource Sharing (CORS) configuration implemented for the Jiroshi Headless LMS.

## The Challenge

We needed a configuration that satisfies three conflicting requirements:
1.  **Open API Platform**: Any developer can build a frontend on *any* domain (localhost, custom domains, etc.).
2.  **Secure Authentication**: We use **HTTP-only cookies** for refresh tokens, which provides better security than storing tokens in localStorage.
3.  **Browser Security Rules**: Browsers strictly forbid using the wildcard `*` for the `Access-Control-Allow-Origin` header when `Access-Control-Allow-Credentials` is set to `true`.

## The Solution: Dynamic Origin Reflection

To allow **any** domain to connect while still supporting secure cookies, we use a regex pattern that matches every origin. This triggers the Django CORS middleware to "reflect" the incoming `Origin` header back in the response, satisfying browser security checks.

### Configuration

In `config/settings.py`:

```python
# CORS SETTINGS
# For headless LMS - DYNAMIC configuration for any custom domain

# 1. Enable credentials (required for HTTP-only cookies)
# This allows the browser to send cookies (like refresh tokens) with cross-origin requests.
CORS_ALLOW_CREDENTIALS = True

# 2. Allow ANY domain dynamically
# The trick: We can't use "Allow All = True" (wildcard *) with credentials.
# Instead, we use a Regex that matches EVERYTHING.
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^.*$",  # Match any origin (http, https, localhost, capacitor, etc.)
]

# Note: We explicitly DO NOT set CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOWED_ORIGINS list is also not needed anymore as the regex covers everything.

# Allowed methods for API requests
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allowed headers (including custom API key header)
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-api-key',
    'x-csrftoken',
    'x-requested-with',
]

# Apply CORS only to headless API routes
CORS_URLS_REGEX = r"^/api/.*$"

# Cookie settings for cross-origin requests
# These are required to allow cookies to be sent across different domains
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = not DEBUG  # True in production (HTTPS required)
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = not DEBUG  # True in production (HTTPS required)
```

## How It Works

1.  **The Request**: A user visits a frontend at `https://my-custom-lms.com` and makes an API call to our backend. The browser sends an `Origin: https://my-custom-lms.com` header.
2.  **The Match**: The backend checks the origin against `CORS_ALLOWED_ORIGIN_REGEXES`. Since `^.*$` matches everything, it evaluates to **True**.
3.  **The Reflection**: Because it found a match (rather than using a generic wildcard), the middleware dynamically constructs the response header:
    *   `Access-Control-Allow-Origin: https://my-custom-lms.com` (Explicitly naming the caller)
    *   `Access-Control-Allow-Credentials: true`
4.  **Browser Acceptance**: The browser sees that the server explicitly whitelisted *this specific site* and allowed credentials. It happily accepts the response and allows the Javascript to see the result.

This setup provides the "Allow All" flexibility of a public API while maintaining the critical "Credentials Allowed" capability needed for cookie-based authentication.
