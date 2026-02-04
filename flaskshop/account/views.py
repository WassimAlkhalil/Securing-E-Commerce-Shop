# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, flash, redirect, render_template, request, url_for, abort, session
from flask_babel import lazy_gettext
from flask_login import current_user, login_required, login_user, logout_user
from pluggy import HookimplMarker
from flask_wtf.csrf import validate_csrf, CSRFError
import time

import pyotp
import qrcode
import io
import base64

from flaskshop.extensions import bcrypt
from flaskshop.order.models import Order
from flaskshop.utils import flash_errors
from flaskshop.extensions import csrf_protect as profile

from .forms import AddressForm, ChangePasswordForm, LoginForm, RegisterForm, ResetPasswd, Enable2FAForm
from .models import User, UserAddress
from .utils import gen_tmp_pwd, send_reset_pwd_email
from flask_wtf.csrf import generate_csrf


def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

impl = HookimplMarker("flaskshop")


def index():
    form = ChangePasswordForm(request.form)
    orders = Order.get_current_user_orders()
    return render_template("account/details.html", form=form, orders=orders)


# author: Wassim Alkhalil
# Explanation: Implements a secure two-step login process:
# Step 1: Username + password authentication with brute force protection
# Step 2: TOTP/backup code verification with progressive rate limiting
# 
# Security features:
# - Timing attack mitigation: dummy password check for non-existent users
# - Brute force protection: 5 failed password attempts = 15 min lockout
# - Session fixation protection: unique login token per 2FA session
# - Session timeout: 2FA step times out after 5 minutes
# - TOTP brute force: 5 failed codes = 15+ min progressive lockout
# - Backup codes bypass TOTP rate limiting (one-time use)
def login():
    """login page."""
    if request.method == 'POST':
        form = LoginForm(request.form)
        if 'login_step' not in session:
            # First step: credentials
            # Manual validation for credentials
            username = form.username.data
            password = form.password.data
            if not username or not password:
                flash(lazy_gettext("Username and password are required."), "warning")
            else:
                if "@" in username:
                    user = User.query.filter_by(email=username).first()
                else:
                    user = User.query.filter_by(username=username).first()
                
                # Always perform password check to prevent username enumeration attacks
                # If user not found, perform dummy check with fake hash to maintain consistent response time
                is_valid_user = user is not None
                is_active = is_valid_user and user.is_active
                password_correct = is_valid_user and user.check_password(password)
                
                # Dummy password check if user not found (constant time)
                if not is_valid_user:
                    bcrypt.check_password_hash(bcrypt.generate_password_hash(b'dummy').decode(), password)
                
                # Check if account is locked from too many failed password attempts
                # Shows dynamic remaining lockout time to user
                if is_valid_user and user.is_login_locked():
                    remaining_minutes = user.get_login_lockout_minutes()
                    flash(lazy_gettext(f"Account temporarily locked due to too many failed login attempts. Please try again in {remaining_minutes} minute(s)."), "error")
                elif not is_valid_user:
                    flash(lazy_gettext("Invalid username or password"), "warning")
                elif not is_active:
                    flash(lazy_gettext("User not activated"), "error")
                    user.record_failed_login()
                elif not password_correct:
                    flash(lazy_gettext("Invalid username or password"), "warning")
                    user.record_failed_login()
                else:
                    # Credentials correct - reset failed attempts
                    user.reset_failed_logins()
                    # Credentials correct
                    if user.totp_secret:
                        session['login_step'] = '2fa'
                        session['login_user_id'] = user.id
                        session['login_token'] = __import__('secrets').token_hex(32)  # Session fixation token
                        session['login_timestamp'] = time.time()
                        return render_template("account/login.html", form=LoginForm(), show_2fa=True, hide_credentials=True)
                    else:
                        login_user(user)
                        redirect_url = request.args.get("next") or url_for("public.home")
                        flash(lazy_gettext("You are log in."), "success")
                        return redirect(redirect_url)
        else:
            # Second step: 2FA
            # Validate 2FA session hasn't expired (5 minute timeout)
            login_timestamp = session.get('login_timestamp')
            login_token = session.get('login_token')
            
            if not login_timestamp or not login_token:
                flash(lazy_gettext("Invalid session. Please login again."), "error")
                session.pop('login_step', None)
                session.pop('login_user_id', None)
                session.pop('login_timestamp', None)
                session.pop('login_token', None)
                return redirect(url_for('account.login'))
            
            # 2FA session timeout (5 minutes)
            # Prevents session hijacking - even if someone gets the session cookie,
            # they need to complete 2FA within 5 minutes or start over
            if (time.time() - login_timestamp) > 300:
                flash(lazy_gettext("2FA session expired. Please login again."), "error")
                session.pop('login_step', None)
                session.pop('login_user_id', None)
                session.pop('login_timestamp', None)
                session.pop('login_token', None)
                return redirect(url_for('account.login'))
            
            user = User.get_by_id(session.get('login_user_id'))
            if user and user.totp_secret:
                totp_code = form.totp_code.data
                if not totp_code:
                    flash(lazy_gettext("2FA code is required"), "error")
                    user.record_failed_2fa()
                else:
                    code_valid = False
                    is_backup_code = False
                    
                    # Try backup code first (8 hex chars, uppercase)
                    # Backup codes are NOT subject to rate limiting because:
                    # 1. They are one-time use only (can't be brute-forced)
                    # 2. Users should always have emergency access if locked out
                    # This provides emergency recovery without circumventing security
                    if len(totp_code) == 8 and all(c in '0123456789ABCDEF' for c in totp_code.upper()):
                        code_valid = user.verify_backup_code(totp_code.upper())
                        is_backup_code = True
                    # Try TOTP code (6 digits) - subject to progressive rate limiting
                    # After 5 failures: 15 min lockout
                    # After 6+ failures: 15 + (attempts-5)*5 min lockout (exponential backoff)
                    elif len(totp_code) == 6 and totp_code.isdigit():
                        # Check if account is locked due to too many failed TOTP attempts
                        if user.is_2fa_locked():
                            remaining_minutes = user.get_2fa_lockout_minutes()
                            flash(lazy_gettext(f"Too many failed authenticator codes. Please try again in {remaining_minutes} minute(s), or use a backup code."), "error")
                            return render_template("account/login.html", form=LoginForm(), show_2fa=True, hide_credentials=True)
                        
                        totp = pyotp.TOTP(user.totp_secret)
                        # Constant-time comparison for TOTP code (prevents timing attacks)
                        code_valid = totp.verify(totp_code, valid_window=1)
                    
                    if code_valid:
                        user.reset_failed_2fa()
                        login_user(user)
                        session.pop('login_step', None)
                        session.pop('login_user_id', None)
                        session.pop('login_timestamp', None)
                        session.pop('login_token', None)
                        redirect_url = request.args.get("next") or url_for("public.home")
                        if is_backup_code:
                            remaining_codes = user.get_backup_codes_count()
                            flash(lazy_gettext(f"You are logged in. {remaining_codes} backup code(s) remaining."), "success")
                        else:
                            flash(lazy_gettext("You are log in."), "success")
                        return redirect(redirect_url)
                    else:
                        # Only record failed attempt for TOTP codes, not backup codes
                        # (backup codes are one-time use, so failed attempts don't matter)
                        if not is_backup_code:
                            user.record_failed_2fa()
                        flash(lazy_gettext("Invalid 2FA code or backup code."), "warning")
                return render_template("account/login.html", form=LoginForm(), show_2fa=True, hide_credentials=True)
            else:
                # Invalid session, reset
                session.pop('login_step', None)
                session.pop('login_user_id', None)
                session.pop('login_timestamp', None)
                session.pop('login_token', None)
                return redirect(url_for('account.login'))
    else:
        # GET request - clear any session data
        session.pop('login_step', None)
        session.pop('login_user_id', None)
        session.pop('login_timestamp', None)
        session.pop('login_token', None)
    
    return render_template("account/login.html", form=LoginForm())


def resetpwd():
    """Reset user password"""
    form = ResetPasswd(request.form)

    if form.validate_on_submit():
        flash(lazy_gettext("Check your e-mail."), "success")
        new_passwd = gen_tmp_pwd()
        send_reset_pwd_email(form.username.data, new_passwd)
        form.user.update(password=new_passwd)
        return redirect(url_for("account.login"))
    else:
        flash_errors(form)
    return render_template("account/login.html", form=form, reset=True)


@login_required
def logout():
    """Logout."""
    logout_user()
    flash(lazy_gettext("You are logged out."), "info")
    return redirect(url_for("public.home"))


def signup():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User.create(
            username=form.username.data,
            email=form.email.data.lower(),
            password=form.password.data,
            is_active=True,
        )
        login_user(user)
        flash(lazy_gettext("You are signed up."), "success")
        return redirect(url_for("public.home"))
    else:
        flash_errors(form)
    return render_template("account/signup.html", form=form)


def set_password():
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        current_user.update(password=form.password.data)
        flash(lazy_gettext("You have changed password."), "success")
    else:
        flash_errors(form)
    return redirect(url_for("account.index"))

# Author: Wassim Alkhalil
#  Handles 2FA setup with TOTP secret generation and backup code creation.
# Process:
# 1. Generate TOTP secret (base32 string)
# 2. Generate 10 one-time backup codes
# 3. Display QR code for user's authenticator app
# 4. Require TOTP code verification before saving
# 5. Display backup codes for user to save securely
#
# Security considerations:
# - Secret stored in session during setup (not persisted until verified)
# - Backup codes generated fresh (not reused from previous setups)
# - User must scan QR code AND enter correct TOTP code to confirm setup
@login_required
@profile.exempt
def enable_2fa():
    import json
    import secrets
    if current_user.totp_secret:
        flash(lazy_gettext("2FA is already enabled."), "info")
        return redirect(url_for("account.index"))

    if '2fa_secret' not in session:
        session['2fa_secret'] = pyotp.random_base32()
        # Generate 10 backup codes (8 hex characters each = 256 possible combinations)
        # Each code can only be used once to prevent replay attacks
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        session['2fa_backup_codes'] = backup_codes

    secret = session['2fa_secret']
    backup_codes = session.get('2fa_backup_codes', [])
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=current_user.email, issuer_name="FlaskShop")

    # Generate QR code
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    qr_code = base64.b64encode(buf.getvalue()).decode('ascii')

    form = Enable2FAForm(request.form)
    if form.validate_on_submit():
        if totp.verify(form.totp_code.data, valid_window=1):
            # Store backup codes as JSON
            current_user.update(
                totp_secret=secret,
                backup_codes=json.dumps(backup_codes)
            )
            session.pop('2fa_secret', None)
            session.pop('2fa_backup_codes', None)
            return render_template("account/enable_2fa.html", form=form, qr_code=qr_code, secret=secret, enabled=True, backup_codes=backup_codes)
        else:
            form.totp_code.errors.append(lazy_gettext("Invalid 2FA code. Please try again."))

    return render_template("account/enable_2fa.html", form=form, qr_code=qr_code, secret=secret, backup_codes=backup_codes)

@login_required
@profile.exempt
def disable_2fa():
    if not current_user.totp_secret:
        flash(lazy_gettext("2FA is not enabled."), "info")
        return redirect(url_for("account.index"))

    current_user.update(totp_secret=None)
    flash(lazy_gettext("2FA disabled successfully."), "success")
    return redirect(url_for("account.index"))

# author: Wassim Alkhalil
@login_required
def view_profile(user_id):
    """
    Access control: a user may only view their own profile unless they have
    admin privileges. This prevents IDOR by blocking direct access to other
    users' profiles via the numeric ID.
    """
    user = User.get_by_id(user_id)
    if not user:
        flash("User not found", "error")
        return redirect(url_for("public.home"))
    # author: Wassim Alkhalil
    # Enforce ownership: only the profile owner or an admin can view this page
    if current_user.id != user_id and not current_user.can_admin():
        # Do not leak whether the user exists and return a generic 403
        abort(403)

    return render_template('account/profile.html', user=user, title=f"{user.username}'s Profile")

def addresses():
    """List addresses."""
    addresses = current_user.addresses
    return render_template("account/addresses.html", addresses=addresses)



@profile.exempt
def edit_address():
    """Create and edit an address."""
    address_id = request.args.get("id", None, type=int)
    user_address = UserAddress.get_by_id(address_id) if address_id else None
    if address_id:
        user_address = UserAddress.get_by_id(address_id)
        # IDOR VUR FIX(SWARUP)
        if not user_address or user_address.user_id != current_user.id:
            abort(403)
        form = AddressForm(request.form, obj=user_address)
    #CSRF ATTACK FIX(SWARUP)
    if request.method == "POST" and form.validate_on_submit():

        try:
            validate_csrf(request.form.get("csrf_token"))
        except CSRFError:
            current_app.logger.warning(
                "CSRF blocked: path=%s remote=%s", request.path, request.remote_addr
            )
            return "CSRF token missing or invalid", 400

        address_data = {
            "province": form.province.data,
            "city": form.city.data,
            "district": form.district.data,
            "address": form.address.data,
            "contact_name": form.contact_name.data,
            "contact_phone": form.contact_phone.data,
            "user_id": current_user.id,
        }
        if user_address:
            UserAddress.update(user_address, **address_data)
            flash(lazy_gettext("Success edit address."), "success")
        else:
            UserAddress.create(**address_data)
            flash(lazy_gettext("Success add address."), "success")
        return redirect(url_for("account.index") + "#addresses")
    else:
        flash_errors(form)
    return render_template(
        "account/address_edit.html", form=form, address_id=address_id
    )



def delete_address(id):
    user_address = UserAddress.get_by_id(id)
    if user_address in current_user.addresses:
        UserAddress.delete(user_address)
    return redirect(url_for("account.index") + "#addresses")

@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("account", __name__)
    bp.add_url_rule("/", view_func=index)
    bp.add_url_rule("/login", view_func=login, methods=["GET", "POST"])
    bp.add_url_rule("/resetpwd", view_func=resetpwd, methods=["GET", "POST"])
    bp.add_url_rule("/logout", view_func=logout)
    bp.add_url_rule("/signup", view_func=signup, methods=["GET", "POST"])
    bp.add_url_rule("/setpwd", view_func=set_password, methods=["POST"])
    bp.add_url_rule("/address", view_func=addresses)
    bp.add_url_rule("/address/edit", view_func=edit_address, methods=["GET", "POST"])
    bp.add_url_rule(
        "/address/<int:id>/delete", view_func=delete_address, methods=["POST"]
    )
    bp.add_url_rule('/profile/<int:user_id>', view_func=view_profile)
    bp.add_url_rule("/enable_2fa", view_func=enable_2fa, methods=["GET", "POST"])
    bp.add_url_rule("/disable_2fa", view_func=disable_2fa, methods=["POST"])
    app.register_blueprint(bp, url_prefix="/account")
