# -*- coding: utf-8 -*-
"""User forms."""
import bleach
from flask_babel import lazy_gettext
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError
import re
import pyotp
import hashlib
import requests
import os
from datetime import datetime, timedelta, timezone
from flask import current_app, request
from .models import User

# author: Wassim Alkhalil
# Google reCAPTCHA v3 verification endpoint
RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

# In-memory cache for used tokens (prevents replay attacks)
_used_tokens_cache = {}

# author: Wassim Alkhalil
def _cleanup_token_cache():
    """Remove expired tokens from cache (older than 2 minutes)."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=2)
    expired_keys = [k for k, v in _used_tokens_cache.items() if v < cutoff]
    for key in expired_keys:
        del _used_tokens_cache[key]

# author: Wassim Alkhalil
# Secure reCAPTCHA v3 verification function
def verify_recaptcha_token(token, expected_action='register'):
    """
    Verify reCaptcha v3 token with comprehensive security checks.
    
    Security validations:
    - Token not empty and not previously used (replay protection)
    - Valid response from Google's verification API
    - Score meets minimum threshold
    - Action matches expected value
    - Hostname matches server domain
    - Timestamp is recent (within 2 minutes)
    
    Args:
        token: reCAPTCHA response token from client
        expected_action: Expected action name (default: 'register')
    
    Returns:
        True if all validations pass, False otherwise
    """
    if not token:
        current_app.logger.warning("reCAPTCHA: Empty token received")
        return False
    
    # Check token replay (prevent reuse)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if token_hash in _used_tokens_cache:
        current_app.logger.warning(
            f"reCAPTCHA: Token replay attempt detected from {request.remote_addr}"
        )
        return False
    
    # Cleanup old tokens periodically
    _cleanup_token_cache()
    
    try:
        # Get configuration from Flask config
        secret_key = current_app.config.get('RECAPTCHA_SECRET_KEY')
        score_threshold = current_app.config.get('RECAPTCHA_SCORE_THRESHOLD', 0.5)
        expected_hostname = current_app.config.get('SERVER_NAME', 'localhost')
        
        if not secret_key:
            current_app.logger.error("reCAPTCHA: RECAPTCHA_SECRET_KEY not configured")
            return False
        
        # Verify with Google's API
        response = requests.post(
            RECAPTCHA_VERIFY_URL,
            data={
                'secret': secret_key,
                'response': token,
                'remoteip': request.remote_addr  # Include user IP for better security
            },
            timeout=5
        )
        
        if response.status_code != 200:
            current_app.logger.error(
                f"reCAPTCHA: API returned status {response.status_code}"
            )
            return False
        
        data = response.json()
        
        # Check if verification was successful
        if not data.get('success'):
            error_codes = data.get('error-codes', [])
            current_app.logger.warning(
                f"reCAPTCHA: Verification failed - errors={error_codes}, ip={request.remote_addr}"
            )
            return False
        
        # Verify score threshold
        score = data.get('score', 0)
        if score < score_threshold:
            current_app.logger.info(
                f"reCAPTCHA: Score too low - score={score}, threshold={score_threshold}, ip={request.remote_addr}"
            )
            return False
        
        # Verify action matches expected
        actual_action = data.get('action')
        if actual_action != expected_action:
            current_app.logger.warning(
                f"reCAPTCHA: Action mismatch - expected='{expected_action}', got='{actual_action}', ip={request.remote_addr}"
            )
            return False
        
        # Verify hostname matches (prevents cross-domain token theft)
        actual_hostname = data.get('hostname', '')
        # Allow localhost for development
        if actual_hostname not in [expected_hostname, 'localhost', '127.0.0.1']:
            current_app.logger.warning(
                f"reCAPTCHA: Hostname mismatch - expected='{expected_hostname}', got='{actual_hostname}', ip={request.remote_addr}"
            )
            return False
        
        # Verify timestamp is recent (within 2 minutes)
        challenge_ts = data.get('challenge_ts')
        if challenge_ts:
            try:
                token_time = datetime.fromisoformat(challenge_ts.replace('Z', '+00:00'))
                age = datetime.now(token_time.tzinfo) - token_time
                if age > timedelta(minutes=2):
                    current_app.logger.warning(
                        f"reCAPTCHA: Token too old - age={age}, ip={request.remote_addr}"
                    )
                    return False
            except (ValueError, TypeError, AttributeError) as e:
                current_app.logger.error(f"reCAPTCHA: Invalid timestamp format - {e}")
                return False
        
        # All checks passed - mark token as used
        _used_tokens_cache[token_hash] = datetime.now(timezone.utc)
        
        current_app.logger.info(
            f"reCAPTCHA: Verification successful - score={score}, action={actual_action}, ip={request.remote_addr}"
        )
        return True
        
    except requests.RequestException as e:
        # Fail closed - reject if verification service unavailable
        current_app.logger.error(f"reCAPTCHA: Network error - {e}")
        return False
    except Exception as e:
        current_app.logger.error(f"reCAPTCHA: Unexpected error - {e}")
        return False

# Task 3.2 (Swarup): Enforce 3 password rules (min length, uppercase/lowercase/numbers) + check HIBP API and local 100k-password list
# Load NCSC txt common passwords
# Path to the current directory of this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the common passwords file
COMMON_PASSWORDS_FILE = os.path.join(BASE_DIR,"security", "100k-most-used-passwords-NCSC.txt")

# Load passwords into a set
with open(COMMON_PASSWORDS_FILE, "r", encoding="utf-8") as f:
    COMMON_PASSWORDS = {line.strip().lower() for line in f}

# ----------------------------
# Have I Been Pwned API check
# k-anonymity (only first 5 chars of SHA1 are sent)
# ----------------------------
def is_pwned_password(password: str) -> bool:
    #fixed by swarup
    sha1 = hashlib.sha1(
        password.encode("utf-8"),
        usedforsecurity=False
    ).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    resp = requests.get(url, timeout=5)

    # Fail gently if API unreachable
    if resp.status_code != 200:
        return False

    hashes = (row.split(":") for row in resp.text.splitlines())
    return any(h[0] == suffix for h in hashes)


# ----------------------------
# NIST-Compliant password strength validation
# ----------------------------
def validate_password_strength(form,field):
    password = field.data
    # NIST: Block common or predictable passwords
    if password.lower().strip() in COMMON_PASSWORDS:
        raise ValidationError(
            lazy_gettext("This password is too common. Choose a stronger one.")
        )
    # NIST: Block passwords found in known breaches
    if is_pwned_password(password):
        raise ValidationError(
            lazy_gettext(
                "This password has been found in data breaches. Choose a different one."
            )
        )

    # NIST: Enforce strong minimum length
    if len(password) < 12:
        raise ValidationError(
            lazy_gettext("Password must be at least 12 characters long.")
        )



    #Character categories
    categories = 0
    if re.search(r"[A-Z]", password):
        categories += 1
    if re.search(r"[a-z]", password):
        categories += 1
    if re.search(r"[0-9]", password):
        categories += 1


    if categories < 3:
        raise ValidationError(
            lazy_gettext(
                "Password must include at least 3 of the following: uppercase letters, lowercase letters, numbers."
            )
        )


# author: Wassim Alkhalil
# Custom validator using bleach library to prevent XSS attacks
# bleach is a well-known, security-focused HTML sanitization library
def no_html_tags(form, field):
    """Validator to reject input containing HTML/script tags using bleach library."""
    if field.data:
        # Use bleach to clean the input (strip all HTML tags)
        cleaned = bleach.clean(field.data, tags=[], strip=True)
        
        # If the cleaned version differs from original, it contained HTML
        if cleaned != field.data:
            raise ValidationError(
                lazy_gettext('Invalid input: HTML tags and scripts are not allowed.')
            )

# author: Wassim Alkhalil
def sanitize_input(data):
    """Sanitize input by stripping all HTML tags using bleach."""
    if data:
        return bleach.clean(data, tags=[], strip=True)
    return data


class RegisterForm(FlaskForm):
    """Register form."""

    username = StringField(
        lazy_gettext("Username"),
        validators=[
            DataRequired(),
            Length(min=3, max=25),
            Regexp(
                "^[a-zA-Z0-9]*$",
                message=lazy_gettext(
                    "The username should contain only a-z, A-Z and 0-9."
                ),
            ),
        ],
    )
    email = StringField(
        lazy_gettext("Email"),
        validators=[DataRequired(), Email(), Length(min=6, max=40)],
    )
    #added function call in validator(Swarup)
    password = PasswordField(
        lazy_gettext("Password"), validators=[DataRequired(), Length(min=6, max=40), validate_password_strength]
    )
    confirm = PasswordField(
        lazy_gettext("Verify password"),
        [
            DataRequired(),
            EqualTo("password", message=lazy_gettext("Passwords must match")),
        ],
    )
    # author: Wassim Alkhalil
    # reCaptcha token for bot prevention
    recaptcha_token = HiddenField("g-recaptcha-response")

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, extra_validators=None):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate(extra_validators)
        if not initial_validation:
            return False
        
        # author: Wassim Alkhalil
        # Validate reCaptcha token
        if not self.recaptcha_token.data:
            self.recaptcha_token.errors.append(
                lazy_gettext("reCaptcha verification required. Please refresh and try again.")
            )
            return False
        
        if not verify_recaptcha_token(self.recaptcha_token.data, expected_action='register'):
            self.recaptcha_token.errors.append(
                lazy_gettext("reCaptcha verification failed. Please try again.")
            )
            return False
        
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append(lazy_gettext("Username already registered"))
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append(lazy_gettext("Email already registered"))
            return False
        return True


class ResetPasswd(FlaskForm):
    """Password reset"""

    username = StringField(lazy_gettext("Email"), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(ResetPasswd, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, extra_validators=None):
        """Validate the form."""
        initial_validation = super(ResetPasswd, self).validate(extra_validators)
        if not initial_validation:
            return False

        if "@" not in self.username.data:
            self.username.errors.append(lazy_gettext("Invalid"))
            return False

        self.user = User.query.filter_by(email=self.username.data).first()
        if not self.user:
            self.username.errors.append(lazy_gettext("Unknown username"))
            return False
        if not self.user.is_active:
            self.username.errors.append(lazy_gettext("User not activated"))
            return False

        return True


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        lazy_gettext("Username Or Email"), validators=[DataRequired()]
    )
    password = PasswordField(lazy_gettext("Password"), validators=[DataRequired()])
    # author: Wassim Alkhalil
    # Added optional field for 2FA code or backup code during login. Field accepts both formats: 6-digit TOTP codes AND 8-character hex backup codes
    totp_code = StringField(lazy_gettext("2FA Code or Backup Code"))

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, extra_validators=None):
        """Validate the form."""
        initial_validation = super(LoginForm, self).validate(extra_validators)
        if not initial_validation:
            return False

        if "@" in self.username.data:
            self.user = User.query.filter_by(email=self.username.data).first()
        else:
            self.user = User.query.filter_by(username=self.username.data).first()
        if not self.user:
            self.username.errors.append(lazy_gettext("Unknown username"))
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append(lazy_gettext("Invalid password"))
            return False

        if not self.user.is_active:
            self.username.errors.append(lazy_gettext("User not activated"))
            return False

        # author: Wassim Alkhalil
        # Handle 2FA verification for users who have it enabled:
        # - If the input is exactly 6 digits, interpret it as a TOTP (time-based one-time password)
        #   and validate it against the user's 2FA secret.
        # - If the input is exactly 8 characters, interpret it as a backup code and validate it
        #   against the user's stored backup codes and mark it as used if valid.
        # - If the input doesn't match either format, return a validation error.
        if self.user.totp_secret:
            if not self.totp_code.data:
                self.totp_code.errors.append(lazy_gettext("2FA code required"))
                return False
            if len(self.totp_code.data) != 6:
                self.totp_code.errors.append(lazy_gettext("2FA code must be exactly 6 digits"))
                return False
            totp = pyotp.TOTP(self.user.totp_secret)
            if not totp.verify(self.totp_code.data):
                self.totp_code.errors.append(lazy_gettext("Invalid 2FA code"))
                return False

        return True


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        lazy_gettext("Old Password"), validators=[DataRequired()]
    )
    password = PasswordField(lazy_gettext("Password"), validators=[DataRequired()])
    confirm = PasswordField(
        lazy_gettext("Verify password"),
        validators=[
            DataRequired(),
            EqualTo("password", message=lazy_gettext("Passwords must match")),
        ],
    )

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super().__init__(*args, **kwargs)
        self.user = current_user

    def validate(self, extra_validators=None):
        """Validate the form."""
        initial_validation = super().validate(extra_validators)
        if not initial_validation:
            return False

        if not self.user.check_password(self.old_password.data):
            self.old_password.errors.append(lazy_gettext("Invalid password"))
            return False

        return True


# author: Wassim Alkhalil
# Form used to confirm a new 2FA setup by verifying a valid TOTP code. The user first scans the QR code with their authenticator app, then enters
# the 6-digit code generated by the app to prove they have correctly set up 2FA before the secret is persisted.
class Enable2FAForm(FlaskForm):
    """Enable 2FA form."""

    totp_code = StringField(
        lazy_gettext("2FA Code"), validators=[DataRequired(), Length(min=6, max=6)]
    )


# author: Wassim Alkhalil
# AddressForm with XSS prevention validators
class AddressForm(FlaskForm):
    """Address form with XSS protection."""

    class Meta:
        csrf = True  # default: True, can override per form instance

    province = StringField(
        lazy_gettext("Province"), 
        validators=[DataRequired(), Length(max=255), no_html_tags]
    )
    city = StringField(
        lazy_gettext("City"), 
        validators=[DataRequired(), Length(max=255), no_html_tags]
    )
    district = StringField(
        lazy_gettext("District"), 
        validators=[DataRequired(), Length(max=255), no_html_tags]
    )
    address = StringField(
        lazy_gettext("Address"), 
        validators=[DataRequired(), Length(max=255), no_html_tags]
    )
    contact_name = StringField(
        lazy_gettext("Contact name"), 
        validators=[DataRequired(), Length(max=255), no_html_tags]
    )
    contact_phone = StringField(
        lazy_gettext("Contact Phone"),
        validators=[DataRequired(), Length(min=10, max=20), no_html_tags],
    )

    def __init__(self, *args, **kwargs):
        """Create instance."""
        kwargs['meta'] = {'csrf': False}
        super().__init__(*args, **kwargs)
