"""
Security Middleware for PharmTrace
Provides additional security layers for the pharmaceutical tracking system.
"""

import logging
import time
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from .security import SECURITY_HEADERS, check_rate_limit, increment_login_attempts

# Configure security logging
security_logger = logging.getLogger('pharmatrace.security')

class SecurityMiddleware(MiddlewareMixin):
    """
    Custom security middleware for PharmTrace application.
    """
    
    def process_request(self, request):
        """Process incoming requests for security checks."""
        
        # Add security headers
        for header, value in SECURITY_HEADERS.items():
            request.META[f'HTTP_{header.upper().replace("-", "_")}'] = value
        
        # Check for suspicious patterns in URLs
        suspicious_patterns = [
            '../', '..\\', 'script', 'javascript:', 'vbscript:', 'onload', 'onerror',
            'eval(', 'expression(', '<script', '</script>', 'document.cookie',
            'union select', 'drop table', 'delete from', 'insert into'
        ]
        
        url_path = request.get_full_path().lower()
        for pattern in suspicious_patterns:
            if pattern in url_path:
                security_logger.warning(f"Suspicious URL pattern detected: {pattern} from IP: {self.get_client_ip(request)}")
                return HttpResponseForbidden("Access denied: Suspicious request pattern detected")
        
        # Rate limiting for login attempts
        if request.path == '/login/' and request.method == 'POST':
            client_ip = self.get_client_ip(request)
            if not check_rate_limit(client_ip):
                security_logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return HttpResponseForbidden("Too many login attempts. Please try again later.")
        
        return None
    
    def process_response(self, request, response):
        """Add security headers to response."""
        for header, value in SECURITY_HEADERS.items():
            response[header] = value
        
        # Remove server information
        if 'Server' in response:
            del response['Server']
        
        # Add custom security headers
        response['X-Powered-By'] = 'PharmTrace-Secure'
        response['X-Robots-Tag'] = 'noindex, nofollow, nosnippet, noarchive'
        
        return response
    
    def get_client_ip(self, request):
        """Get the real client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Session security middleware to handle session timeouts and security.
    """
    
    def process_request(self, request):
        """Check session security."""
        
        # Skip security checks for static files and public pages
        exempt_paths = ['/static/', '/media/', '/', '/login/', '/register/']
        if any(request.path.startswith(path) for path in exempt_paths):
            return None
        
        # Check if user is authenticated via session
        if not request.session.get('username'):
            # Redirect to login for protected pages
            if request.path not in ['/login/', '/register/', '/']:
                return redirect('traceability:login')
        
        # Session timeout check
        last_activity = request.session.get('last_activity')
        if last_activity:
            if time.time() - last_activity > 1800:  # 30 minutes
                request.session.flush()
                security_logger.info(f"Session expired for user: {request.session.get('username', 'Unknown')}")
                return redirect('traceability:login')
        
        # Update last activity
        request.session['last_activity'] = time.time()
        
        return None

class CSRFProtectionMiddleware(MiddlewareMixin):
    """
    Enhanced CSRF protection middleware.
    """
    
    def process_request(self, request):
        """Enhanced CSRF validation."""
        
        # Skip CSRF for GET requests and exempt paths
        if request.method == 'GET' or request.path in ['/login/', '/']:
            return None
        
        # Check for CSRF token in POST requests
        if request.method == 'POST':
            csrf_token = request.POST.get('csrfmiddlewaretoken') or request.META.get('HTTP_X_CSRFTOKEN')
            if not csrf_token:
                security_logger.warning(f"Missing CSRF token from IP: {self.get_client_ip(request)}")
                return HttpResponseForbidden("CSRF token missing")
        
        return None
    
    def get_client_ip(self, request):
        """Get the real client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class InputValidationMiddleware(MiddlewareMixin):
    """
    Input validation middleware to sanitize user inputs.
    """
    
    def process_request(self, request):
        """Validate and sanitize user inputs."""
        
        # Define maximum input lengths
        max_lengths = {
            'username': 50,
            'password': 128,
            'name': 100,
            'description': 1000,
            'price': 20,
            'quantity': 10
        }
        
        # Validate POST data
        if request.method == 'POST':
            for key, value in request.POST.items():
                if isinstance(value, str):
                    # Check for maximum length
                    max_len = max_lengths.get(key, 500)
                    if len(value) > max_len:
                        security_logger.warning(f"Input too long for field {key}: {len(value)} characters")
                        return HttpResponseForbidden(f"Input too long for field {key}")
                    
                    # Check for malicious patterns
                    malicious_patterns = [
                        '<script', '</script>', 'javascript:', 'vbscript:', 'onload=',
                        'onerror=', 'eval(', 'expression(', 'document.cookie',
                        'union select', 'drop table', 'delete from', 'insert into',
                        '--', ';--', '/*', '*/', 'xp_', 'sp_'
                    ]
                    
                    value_lower = value.lower()
                    for pattern in malicious_patterns:
                        if pattern in value_lower:
                            security_logger.warning(f"Malicious pattern detected in {key}: {pattern}")
                            return HttpResponseForbidden("Invalid input detected")
        
        return None
