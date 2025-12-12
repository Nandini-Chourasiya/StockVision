"""
StockVision - Authentication Blueprint
Handles user registration, login, logout, and session management
"""
import os
import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioRestException
from database import db
from models import User, ActivityLog

# Create blueprint
auth_bp = Blueprint('auth', __name__)


# ============================================
# Authentication Decorators
# ============================================
def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('landing'))
        
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get the current logged-in user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


# ============================================
# SMS Login Notification Helper
# ============================================
def send_login_sms(user):
    """
    Send SMS notification on successful login.
    Falls back to console logging if Twilio is not configured (mock mode).
    Fails silently - login should succeed even if SMS fails.
    """
    sms_message = "You just logged in to your StockVision account."
    
    try:
        # Check if user has phone number
        if not user.phone_number:
            print(f"\n{'='*60}")
            print(f"[MOCK SMS - No phone number for {user.email}]")
            print(f"{'='*60}\n")
            return
        
        # Get Twilio config from environment
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        from_number = os.environ.get('TWILIO_PHONE_NUMBER')
        
        # Check if Twilio is configured - if not, use mock mode
        if not all([account_sid, auth_token, from_number]):
            # MOCK MODE - Print to console instead of sending real SMS
            print(f"\n{'='*60}")
            print(f"[MOCK SMS] Login notification")
            print(f"{'='*60}")
            print(f"   To: {user.phone_number}")
            print(f"   Message: {sms_message}")
            print(f"{'='*60}")
            print(f"   INFO: Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,")
            print(f"         and TWILIO_PHONE_NUMBER to send real SMS")
            print(f"{'='*60}\n")
            return
        
        # Send real SMS via Twilio
        client = TwilioClient(account_sid, auth_token)
        client.messages.create(
            body=sms_message,
            from_=from_number,
            to=user.phone_number
        )
        print(f"\n[SMS SENT] Login notification sent to {user.phone_number}\n")
        
    except TwilioRestException as e:
        print(f"\n[SMS ERROR] Twilio error: {e}\n")
    except Exception as e:
        print(f"\n[SMS ERROR] {e}\n")


# ============================================
# Login Routes
# ============================================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    # Redirect if already logged in
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.is_admin():
            return redirect(url_for('dashboards.admin_dashboard'))
        return redirect(url_for('dashboards.user_dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Validate input
        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return render_template('login.html')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Check if user is active
            if not user.is_active:
                flash('Your account has been deactivated. Please contact admin.', 'error')
                return render_template('login.html')
            
            # Set session
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            session.permanent = True
            
            # Log activity
            log = ActivityLog(
                user_id=user.id,
                action='login',
                details=f'User logged in from {request.remote_addr}'
            )
            db.session.add(log)
            db.session.commit()
            
            # Send SMS notification (non-blocking)
            send_login_sms(user)
            
            flash(f'Welcome back, {user.name}!', 'success')
            
            # Redirect based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.is_admin():
                return redirect(url_for('dashboards.admin_dashboard'))
            return redirect(url_for('dashboards.user_dashboard'))
        
        flash('Invalid email or password.', 'error')
    
    return render_template('login.html')


# ============================================
# Registration Routes
# ============================================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('dashboards.user_dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        
        if not email or '@' not in email:
            errors.append('Please provide a valid email address.')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            errors.append('An account with this email already exists.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role='user',
            is_active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log activity
        log = ActivityLog(
            user_id=user.id,
            action='register',
            details='New user registered'
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


# ============================================
# Logout Route
# ============================================
@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    user_id = session.get('user_id')
    
    if user_id:
        # Log activity
        log = ActivityLog(
            user_id=user_id,
            action='logout',
            details='User logged out'
        )
        db.session.add(log)
        db.session.commit()
    
    # Clear session
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))



# ============================================
# Profile Route
# ============================================
@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Handle user profile view and update"""
    user = get_current_user()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone_number = request.form.get('phone_number', '').strip()
        
        # Validation
        if not name or len(name) < 2:
            flash('Name must be at least 2 characters.', 'error')
            return render_template('profile.html', user=user)
            
        if not email or '@' not in email:
            flash('Please provide a valid email.', 'error')
            return render_template('profile.html', user=user)
        
        # Validate phone number format (E.164)
        if phone_number and not phone_number.startswith('+'):
            flash('Phone number must start with + (E.164 format).', 'error')
            return render_template('profile.html', user=user)
            
        # Check email uniqueness if changed
        if email != user.email:
            existing = User.query.filter_by(email=email).first()
            if existing:
                flash('This email is already in use.', 'error')
                return render_template('profile.html', user=user)
        
        # Update user
        user.name = name
        user.email = email
        user.phone_number = phone_number if phone_number else None
        db.session.commit()
        
        # Update session
        session['user_name'] = name
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('profile.html', user=user)


# ============================================
# Context Processor - Make user available in templates
# ============================================
@auth_bp.app_context_processor
def inject_user():
    """Inject current user into all templates"""
    return {
        'current_user': get_current_user(),
        'is_authenticated': 'user_id' in session
    }
