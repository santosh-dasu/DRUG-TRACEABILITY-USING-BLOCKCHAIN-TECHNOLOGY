"""
Custom validators for PharmTrace pharmaceutical security standards.
"""

import re
import string
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class PharmaceuticalPasswordValidator:
    """
    Validates passwords according to pharmaceutical industry security standards.
    
    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter  
    - At least one digit
    - At least one special character
    - Cannot contain common pharmaceutical terms
    - Cannot contain user information
    """
    
    def __init__(self):
        self.min_length = 12
        self.forbidden_patterns = [
            'password', 'admin', 'pharma', 'drug', 'medicine', 'pill',
            'tablet', 'capsule', 'dose', 'prescription', 'rx', 'fda',
            'dea', '123456', 'qwerty', 'abc123', 'password123'
        ]
    
    def validate(self, password, user=None):
        """Validate password against pharmaceutical security standards."""
        errors = []
        
        # Length check
        if len(password) < self.min_length:
            errors.append(
                ValidationError(
                    f"Password must be at least {self.min_length} characters long.",
                    code='password_too_short',
                )
            )
        
        # Character type requirements
        if not any(c.isupper() for c in password):
            errors.append(
                ValidationError(
                    "Password must contain at least one uppercase letter (A-Z).",
                    code='password_no_upper',
                )
            )
        
        if not any(c.islower() for c in password):
            errors.append(
                ValidationError(
                    "Password must contain at least one lowercase letter (a-z).",
                    code='password_no_lower',
                )
            )
        
        if not any(c.isdigit() for c in password):
            errors.append(
                ValidationError(
                    "Password must contain at least one number (0-9).",
                    code='password_no_digit',
                )
            )
        
        if not any(c in string.punctuation for c in password):
            errors.append(
                ValidationError(
                    "Password must contain at least one special character (!@#$%^&* etc.).",
                    code='password_no_symbol',
                )
            )
        
        # Check for forbidden patterns
        password_lower = password.lower()
        for pattern in self.forbidden_patterns:
            if pattern in password_lower:
                errors.append(
                    ValidationError(
                        f"Password cannot contain common terms like '{pattern}'.",
                        code='password_common_terms',
                    )
                )
        
        # Check for user information (if user provided)
        if user:
            user_info = [
                user.username.lower() if hasattr(user, 'username') else '',
                user.first_name.lower() if hasattr(user, 'first_name') else '',
                user.last_name.lower() if hasattr(user, 'last_name') else '',
                user.email.split('@')[0].lower() if hasattr(user, 'email') and user.email else '',
            ]
            
            for info in user_info:
                if info and len(info) > 2 and info in password_lower:
                    errors.append(
                        ValidationError(
                            "Password cannot contain your personal information.",
                            code='password_too_similar',
                        )
                    )
        
        # Check for sequential characters
        if self._has_sequential_chars(password):
            errors.append(
                ValidationError(
                    "Password cannot contain sequential characters (like 123 or abc).",
                    code='password_sequential',
                )
            )
        
        # Check for repeated characters
        if self._has_repeated_chars(password):
            errors.append(
                ValidationError(
                    "Password cannot have more than 2 repeated characters in a row.",
                    code='password_repeated',
                )
            )
        
        if errors:
            raise ValidationError(errors)
    
    def _has_sequential_chars(self, password):
        """Check for sequential characters like 123, abc, qwe."""
        sequential_patterns = [
            '123', '234', '345', '456', '567', '678', '789',
            'abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi',
            'qwe', 'wer', 'ert', 'rty', 'tyu', 'yui', 'uio'
        ]
        
        password_lower = password.lower()
        for pattern in sequential_patterns:
            if pattern in password_lower or pattern[::-1] in password_lower:
                return True
        return False
    
    def _has_repeated_chars(self, password):
        """Check for repeated characters like aaa, 111."""
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return True
        return False
    
    def get_help_text(self):
        """Return help text for password requirements."""
        return _(
            "Your password must meet pharmaceutical industry security standards:\n"
            f"• At least {self.min_length} characters long\n"
            "• Include uppercase letters (A-Z)\n"
            "• Include lowercase letters (a-z)\n"
            "• Include numbers (0-9)\n"
            "• Include special characters (!@#$%^&*)\n"
            "• Avoid common terms and personal information\n"
            "• No sequential or repeated characters"
        )

class UsernameValidator:
    """
    Validates usernames for pharmaceutical security standards.
    """
    
    def __init__(self):
        self.min_length = 4
        self.max_length = 30
        self.allowed_chars = re.compile(r'^[a-zA-Z0-9._-]+$')
    
    def validate(self, username):
        """Validate username format and security."""
        errors = []
        
        # Length validation
        if len(username) < self.min_length:
            errors.append(f"Username must be at least {self.min_length} characters long.")
        
        if len(username) > self.max_length:
            errors.append(f"Username cannot exceed {self.max_length} characters.")
        
        # Character validation
        if not self.allowed_chars.match(username):
            errors.append("Username can only contain letters, numbers, periods, underscores, and hyphens.")
        
        # Cannot start or end with special characters
        if username.startswith(('.', '_', '-')) or username.endswith(('.', '_', '-')):
            errors.append("Username cannot start or end with special characters.")
        
        # Cannot be all numbers
        if username.isdigit():
            errors.append("Username cannot be all numbers.")
        
        # Reserved usernames
        reserved_names = [
            'admin', 'administrator', 'root', 'system', 'api', 'www',
            'mail', 'ftp', 'test', 'guest', 'anonymous', 'null',
            'pharmatrace', 'support', 'help', 'info', 'service'
        ]
        
        if username.lower() in reserved_names:
            errors.append("This username is reserved and cannot be used.")
        
        if errors:
            raise ValidationError(errors)
        
        return True
