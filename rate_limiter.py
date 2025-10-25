"""
Rate Limiting Middleware
Simple in-memory rate limiter for API endpoints.
For production, use Redis-backed rate limiting (Flask-Limiter with Redis).
"""

from functools import wraps
from flask import request, jsonify
import time
from collections import defaultdict
from threading import Lock

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Identifier for rate limiting (e.g., IP address)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        
        Returns:
            True if request is allowed, False otherwise
        """
        with self.lock:
            now = time.time()
            cutoff = now - window_seconds
            
            # Clean old requests
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]
            
            # Check limit
            if len(self.requests[key]) >= max_requests:
                return False
            
            # Add current request
            self.requests[key].append(now)
            return True
    
    def get_retry_after(self, key: str, window_seconds: int) -> int:
        """Get seconds until rate limit resets."""
        with self.lock:
            if not self.requests[key]:
                return 0
            oldest = min(self.requests[key])
            retry_after = int(window_seconds - (time.time() - oldest))
            return max(0, retry_after)


# Global rate limiter instance
limiter = RateLimiter()


def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """
    Rate limiting decorator.
    
    Usage:
        @app.route('/api/endpoint')
        @rate_limit(max_requests=10, window_seconds=60)
        def endpoint():
            ...
    
    Args:
        max_requests: Maximum requests allowed in window (default: 10)
        window_seconds: Time window in seconds (default: 60)
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get client identifier (IP address)
            client_id = request.headers.get('X-Forwarded-For', request.remote_addr)
            
            if not limiter.is_allowed(client_id, max_requests, window_seconds):
                retry_after = limiter.get_retry_after(client_id, window_seconds)
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Maximum {max_requests} requests per {window_seconds} seconds.',
                    'retry_after': retry_after
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(retry_after)
                return response
            
            return f(*args, **kwargs)
        return wrapped
    return decorator


# Production rate limiter using Flask-Limiter with Redis
"""
For production, install and use Flask-Limiter with Redis:

pip install Flask-Limiter redis

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/ask', methods=['POST'])
@limiter.limit("10 per minute")
def ask():
    ...
"""
