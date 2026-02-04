from functools import reduce
from operator import or_

from flask_login import UserMixin
from libgravatar import Gravatar
from sqlalchemy.ext.hybrid import hybrid_property

from flaskshop.constant import Permission
from flaskshop.database import Column, Model, db
from flaskshop.extensions import bcrypt
from datetime import datetime, timedelta, timezone

class User(Model, UserMixin):
    __tablename__ = "account_user"
    username = Column(db.String(80), unique=True, nullable=False, comment="user`s name")
    email = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    _password = db.Column(db.String(255), nullable=False)
    nick_name = Column(db.String(255))
    is_active = Column(db.Boolean(), default=False)
    open_id = Column(db.String(80), index=True)
    session_key = Column(db.String(80), index=True)
    
    # author: Wassim Alkhalil
    # Stores the base32-encoded secret for generating TOTP codes
    totp_secret = Column(db.String(32), nullable=True)
    
    # Backup codes for emergency 2FA access if user loses authenticator app.
    backup_codes = Column(db.Text, nullable=True)
    
    # Brute force protection for password attempts, after 5 failed attempts the account is locked for 15 minutes
    failed_login_attempts = Column(db.Integer(), default=0)
    last_failed_login = Column(db.DateTime(), nullable=True)
    
    # author: Wassim Alkhalil
    # Brute force protection for 2FA attempts (5 attempts = 15+ min progressive lockout)
    failed_2fa_attempts = Column(db.Integer(), default=0)
    last_failed_2fa = Column(db.DateTime(), nullable=True)

    def __init__(self, username, email, password, **kwargs):
        super().__init__(username=username, email=email, password=password, **kwargs)

    def __str__(self):
        return self.username

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = bcrypt.generate_password_hash(value).decode("UTF-8")

    @property
    def avatar(self):
        return Gravatar(self.email).get_image()

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password.encode("utf-8"), value)

    @property
    def addresses(self):
        return UserAddress.query.filter_by(user_id=self.id).all()

    @property
    def is_active_human(self):
        return "Y" if self.is_active else "N"

    @property
    def roles(self):
        at_ids = (
            UserRole.query.with_entities(UserRole.role_id)
            .filter_by(user_id=self.id)
            .all()
        )
        return Role.query.filter(Role.id.in_(id for id, in at_ids)).all()

    def delete(self):
        for addr in self.addresses:
            addr.delete()
        return super().delete()

    def can(self, permissions):
        if not self.roles:
            return False
        all_perms = reduce(or_, map(lambda x: x.permissions, self.roles))
        return all_perms >= permissions

    def can_admin(self):
        return self.can(Permission.ADMINISTER)

    def can_edit(self):
        return self.can(Permission.EDITOR)

    def can_op(self):
        return self.can(Permission.OPERATOR)

    # author: Wassim Alkhalil
    def is_login_locked(self):
        """Check if account is locked due to too many failed login attempts."""

        if self.failed_login_attempts is None:
            self.failed_login_attempts = 0
        
        if self.failed_login_attempts >= 5:
            if not self.last_failed_login:
                return True
            # Unlock after 15 minutes
            if datetime.now() - self.last_failed_login < timedelta(minutes=15):
                return True
            else:
                # Reset counter
                self.update(failed_login_attempts=0)
        return False

    # author: Wassim Alkhalil
    def get_login_lockout_minutes(self):
        """Get remaining login lockout time in minutes. Returns at least 1 minute if locked."""

        if not self.is_login_locked() or not self.last_failed_login:
            return 0
        elapsed = (datetime.now() - self.last_failed_login).total_seconds() / 60
        remaining = max(1, int(15 - elapsed))  # At least 1 minute
        return remaining

    # author: Wassim Alkhalil
    # Records failed password attempt and increments counter.
    def record_failed_login(self):
        """Record a failed login attempt."""
        self.update(
            failed_login_attempts=self.failed_login_attempts + 1,
            last_failed_login=datetime.now()
        )

    # Author: Wassim Alkhalil
    # Resets failed login counter on successful login.
    def reset_failed_logins(self):
        """Reset failed login counter on successful login."""
        self.update(failed_login_attempts=0, last_failed_login=None)

    # author: Wassim Alkhalil
    # Progressive rate limiting for 2FA code attempts. This makes sustained attacks exponentially more expensive.
    def is_2fa_locked(self):
        """Check if account is locked due to too many failed 2FA attempts."""

        if self.failed_2fa_attempts is None:
            self.failed_2fa_attempts = 0
        
        if self.failed_2fa_attempts >= 5:
            if not self.last_failed_2fa:
                return True
            # Calculate dynamic lockout: 15 minutes base + 5 minutes per failed attempt
            lockout_minutes = 15 + (self.failed_2fa_attempts - 5) * 5
            if datetime.now() - self.last_failed_2fa < timedelta(minutes=lockout_minutes):
                return True
            else:
                # Unlock and reset counter
                self.update(failed_2fa_attempts=0, last_failed_2fa=None)
        return False

    # author: Wassim Alkhalil
    # Explanation: Records failed 2FA attempt with timestamp for lockout tracking.
    def record_failed_2fa(self):
        """Record a failed 2FA attempt."""
        self.update(
            failed_2fa_attempts=self.failed_2fa_attempts + 1,
            last_failed_2fa=datetime.now()
        )

    # author: Wassim Alkhalil
    # Clears failed attempts counter on successful 2FA verification.
    def reset_failed_2fa(self):
        """Reset failed 2FA counter on successful verification."""
        self.update(failed_2fa_attempts=0, last_failed_2fa=None)

    # author: Wassim Alkhalil
    # Calculates and displays remaining lockout time to user.
    def get_2fa_lockout_minutes(self):
        """Get remaining lockout time in minutes. Returns at least 1 minute if locked."""

        if not self.is_2fa_locked() or not self.last_failed_2fa:
            return 0
        lockout_minutes = 15 + (self.failed_2fa_attempts - 5) * 5
        elapsed = (datetime.now() - self.last_failed_2fa).total_seconds() / 60
        remaining = max(1, int(lockout_minutes - elapsed))
        return remaining

    # author: Wassim Alkhalil
    # Verifies backup codes and marks them as used.
    def verify_backup_code(self, code):
        """Verify and consume a backup code. Returns True if valid and unused."""
        import json
        if not self.backup_codes:
            return False
        
        try:
            codes = json.loads(self.backup_codes)
        except (json.JSONDecodeError, TypeError):
            return False
        
        if code in codes:
            # Consume the code by removing it
            codes.remove(code)
            self.update(backup_codes=json.dumps(codes))
            return True
        return False

    # author: Wassim Alkhalil
    # Returns count of remaining unused backup codes to inform user how many recovery codes they have left after using one.
    def get_backup_codes_count(self):
        """Get number of remaining backup codes."""
        import json
        if not self.backup_codes:
            return 0
        try:
            codes = json.loads(self.backup_codes)
            return len(codes)
        except (json.JSONDecodeError, TypeError):
            return 0


class UserAddress(Model):
    __tablename__ = "account_address"
    user_id = Column(db.Integer())
    province = Column(db.String(255))
    city = Column(db.String(255))
    district = Column(db.String(255))
    address = Column(db.String(255))
    contact_name = Column(db.String(255))
    contact_phone = Column(db.String(80))

    # author: Wassim Alkhalil
    # Sanitized full_address property to prevent XSS using bleach library
    # bleach is a well-known, security-focused HTML sanitization library
    @property
    def full_address(self):
        import bleach
        return (
            f"{bleach.clean(self.province or '', tags=[], strip=True)}<br>"
            f"{bleach.clean(self.city or '', tags=[], strip=True)}<br>"
            f"{bleach.clean(self.district or '', tags=[], strip=True)}<br>"
            f"{bleach.clean(self.address or '', tags=[], strip=True)}<br>"
            f"{bleach.clean(self.contact_name or '', tags=[], strip=True)}<br>"
            f"{bleach.clean(self.contact_phone or '', tags=[], strip=True)}"
        )

    @hybrid_property
    def user(self):
        return User.get_by_id(self.user_id)

    def __str__(self):
        return self.full_address


class Role(Model):
    __tablename__ = "account_role"
    name = Column(db.String(80), unique=True)
    permissions = Column(db.Integer(), default=Permission.LOGIN)


class UserRole(Model):
    __tablename__ = "account_user_role"
    user_id = Column(db.Integer())
    role_id = Column(db.Integer())
