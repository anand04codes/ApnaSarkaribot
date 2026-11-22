"""
Rate limiting configuration using slowapi.
Protects the API against denial-of-service and brute force abuse.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

