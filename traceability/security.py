"""
Security Configuration for PharmTrace
This file contains security settings and utilities for the pharmaceutical tracking system.
"""

import secrets
import string
import os
from django.conf import settings

# Security Constants
MIN_PASSWORD_LENGTH = 12
MAX_LOGIN_ATTEMPTS = 5
SESSION_TIMEOUT = 1800  # 30 minutes
TOKEN_EXPIRY = 3600     # 1 hour

# Security Headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data:; connect-src 'self';",
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()'
}

def generate_secret_key():
    """Generate a secure secret key for Django."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(64))

def validate_password_strength(password):
    """
    Validate password strength for pharmaceutical industry standards.
    Returns (is_valid, error_message)
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    if not any(c in string.punctuation for c in password):
        return False, "Password must contain at least one special character"
    
    # Check for common patterns
    common_patterns = ['123', 'abc', 'password', 'admin', 'pharma', 'drug']
    password_lower = password.lower()
    for pattern in common_patterns:
        if pattern in password_lower:
            return False, f"Password cannot contain common pattern: {pattern}"
    
    return True, "Password meets security requirements"

def sanitize_input(input_string, max_length=None):
    """
    Sanitize user input to prevent XSS and injection attacks.
    """
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', 'script', 'javascript']
    sanitized = str(input_string)
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Limit length if specified
    if max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

def generate_csrf_token():
    """Generate a secure CSRF token."""
    return secrets.token_urlsafe(32)

def is_safe_redirect_url(url):
    """Check if a redirect URL is safe to prevent open redirect attacks."""
    if not url:
        return False
    
    # Only allow relative URLs or same-origin URLs
    if url.startswith('/') and not url.startswith('//'):
        return True
    
    # Check for same origin
    if hasattr(settings, 'ALLOWED_HOSTS'):
        for host in settings.ALLOWED_HOSTS:
            if url.startswith(f'http://{host}') or url.startswith(f'https://{host}'):
                return True
    
    return False

# Rate limiting storage (in production, use Redis or database)
LOGIN_ATTEMPTS = {}

def check_rate_limit(identifier):
    """Check if user has exceeded login attempts."""
    attempts = LOGIN_ATTEMPTS.get(identifier, 0)
    return attempts < MAX_LOGIN_ATTEMPTS

def increment_login_attempts(identifier):
    """Increment failed login attempts for identifier."""
    LOGIN_ATTEMPTS[identifier] = LOGIN_ATTEMPTS.get(identifier, 0) + 1

def reset_login_attempts(identifier):
    """Reset login attempts after successful login."""
    if identifier in LOGIN_ATTEMPTS:
        del LOGIN_ATTEMPTS[identifier]

# File upload security
ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.pdf', '.txt']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_file_upload(file):
    """Validate uploaded files for security."""
    if not file:
        return False, "No file provided"
    
    # Check file size
    if file.size > MAX_FILE_SIZE:
        return False, f"File size must be less than {MAX_FILE_SIZE / (1024*1024)}MB"
    
    # Check file extension
    file_ext = os.path.splitext(file.name)[1].lower()
    if file_ext not in ALLOWED_FILE_EXTENSIONS:
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_FILE_EXTENSIONS)}"
    
    # Check for executable files
    dangerous_extensions = ['.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js']
    if file_ext in dangerous_extensions:
        return False, "Executable files are not allowed"
    
    return True, "File is valid"
