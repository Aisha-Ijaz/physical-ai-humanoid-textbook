from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI


# Initialize the limiter with storage using memory (for single instance)
# In production, you may want to use redis storage
limiter = Limiter(key_func=get_remote_address)


def add_rate_limiting(app: FastAPI):
    """
    Add rate limiting middleware to the FastAPI application
    """
    # Attach the limiter to the app
    app.state.limiter = limiter
    
    # Override the default rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # You can set default limits here if needed, or define them per route
    return limiter