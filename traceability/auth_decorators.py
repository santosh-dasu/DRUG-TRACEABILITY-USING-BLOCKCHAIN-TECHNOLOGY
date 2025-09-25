"""
Authentication and authorization decorators for PharmTrace security.
"""

import functools
import logging
import time
from django.shortcuts import redirect, render
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.urls import reverse
from .security import check_rate_limit, increment_login_attempts, sanitize_input

# Security logging
security_logger = logging.getLogger('pharmatrace.security')

def require_authentication(view_func):
    """
    Decorator to require user authentication for view access.
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated via session
        if not request.session.get('username'):
            # Log unauthorized access attempt
            client_ip = get_client_ip(request)
            security_logger.warning(f"Unauthorized access attempt to {request.path} from {client_ip}")
            
            # Redirect to login page
            messages.warning(request, 'Please log in to access this page.')
            return redirect('traceability:login')
        
        # Check session timeout
        last_activity = request.session.get('last_activity', 0)
        if time.time() - last_activity > 1800:  # 30 minutes
            request.session.flush()
            security_logger.info(f"Session expired for user: {request.session.get('username', 'Unknown')}")
            messages.info(request, 'Your session has expired. Please log in again.')
            return redirect('traceability:login')
        
        # Update last activity
        request.session['last_activity'] = time.time()
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

def require_admin_role(view_func):
    """
    Decorator to require admin role for view access.
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check authentication first
        if not request.session.get('username'):
            return redirect('traceability:login')
        
        # Check admin role
        user_role = request.session.get('user_role')
        if user_role != 'admin':
            client_ip = get_client_ip(request)
            username = request.session.get('username', 'Unknown')
            security_logger.warning(f"Unauthorized admin access attempt by {username} from {client_ip}")
            
            return render(request, 'traceability/access_denied.html', {
                'message': 'Administrative privileges required to access this page.'
            }, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

def rate_limit(max_attempts=5, window=300):
    """
    Decorator to rate limit view access.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            client_ip = get_client_ip(request)
            
            if not check_rate_limit(client_ip):
                security_logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please try again later.'
                }, status=429)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator

def validate_input(field_rules=None):
    """
    Decorator to validate and sanitize input data.
    
    Args:
        field_rules: Dict of field validation rules
                    {'field_name': {'max_length': 100, 'required': True}}
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST' and field_rules:
                for field_name, rules in field_rules.items():
                    value = request.POST.get(field_name, '')
                    
                    # Check required fields
                    if rules.get('required', False) and not value.strip():
                        messages.error(request, f'{field_name.title()} is required.')
                        return redirect(request.path)
                    
                    # Check max length
                    max_length = rules.get('max_length')
                    if max_length and len(value) > max_length:
                        messages.error(request, f'{field_name.title()} is too long (max {max_length} characters).')
                        return redirect(request.path)
                    
                    # Sanitize input
                    if value:
                        sanitized_value = sanitize_input(value, max_length)
                        request.POST = request.POST.copy()  # Make mutable
                        request.POST[field_name] = sanitized_value
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator

def log_sensitive_action(action_type):
    """
    Decorator to log sensitive actions for audit trail.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            username = request.session.get('username', 'Anonymous')
            client_ip = get_client_ip(request)
            
            # Log before action
            security_logger.info(f"AUDIT: {action_type} attempted by {username} from {client_ip}")
            
            try:
                response = view_func(request, *args, **kwargs)
                
                # Log successful action
                security_logger.info(f"AUDIT: {action_type} completed successfully by {username}")
                
                return response
                
            except Exception as e:
                # Log failed action
                security_logger.error(f"AUDIT: {action_type} failed for {username}: {str(e)}")
                raise
        
        return wrapper
    return decorator

def csrf_protect_ajax(view_func):
    """
    Decorator to protect AJAX views with CSRF validation.
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
            if not csrf_token:
                return JsonResponse({
                    'error': 'CSRF token required'
                }, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

def secure_file_upload(allowed_extensions=None, max_size=5*1024*1024):
    """
    Decorator to secure file upload endpoints.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST' and request.FILES:
                for file_field, uploaded_file in request.FILES.items():
                    # Check file size
                    if uploaded_file.size > max_size:
                        messages.error(request, f'File {uploaded_file.name} is too large (max {max_size//1024//1024}MB)')
                        return redirect(request.path)
                    
                    # Check file extension
                    if allowed_extensions:
                        file_ext = uploaded_file.name.split('.')[-1].lower()
                        if file_ext not in allowed_extensions:
                            messages.error(request, f'File type .{file_ext} not allowed')
                            return redirect(request.path)
                    
                    # Log file upload
                    username = request.session.get('username', 'Anonymous')
                    security_logger.info(f"File upload: {uploaded_file.name} by {username}")
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator

def get_client_ip(request):
    """Get the real client IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def check_password_strength(password):
    """
    Check password strength according to pharmaceutical standards.
    Returns (is_strong, errors)
    """
    errors = []
    
    if len(password) < 12:
        errors.append("Password must be at least 12 characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain uppercase letters")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain lowercase letters")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain numbers")
    
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        errors.append("Password must contain special characters")
    
    # Check for common patterns
    common_patterns = ['123', 'abc', 'password', 'admin', 'pharma']
    for pattern in common_patterns:
        if pattern.lower() in password.lower():
            errors.append(f"Password cannot contain '{pattern}'")
    
    return len(errors) == 0, errors
