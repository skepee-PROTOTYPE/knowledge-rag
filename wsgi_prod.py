"""
Production WSGI Configuration
Secure Flask application configuration for production deployment.
"""

import os
from app import app

# Production configuration
app.config.update(
    DEBUG=False,
    TESTING=False,
    ENV='production',
    # Security
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    # Performance
    SEND_FILE_MAX_AGE_DEFAULT=31536000,
)

# Security headers middleware
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'"
    )
    return response

if __name__ == '__main__':
    # For Cloud Run, we use the built-in Flask server
    # Cloud Run handles load balancing and scaling
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting production server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
