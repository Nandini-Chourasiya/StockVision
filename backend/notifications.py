"""
StockVision - Notifications Blueprint
Handles SMS (Twilio) and Web Push notifications
"""
import os
import json
from flask import Blueprint, request, jsonify, session
from pywebpush import webpush, WebPushException
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioRestException

from database import db
from models import User, PushSubscription
from auth import login_required, get_current_user

# Create blueprint
notifications_bp = Blueprint('notifications', __name__)

# ============================================
# Configuration from Environment Variables
# ============================================
# Twilio
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')  # Your Twilio number

# VAPID for Web Push
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY')
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY')
VAPID_CLAIMS_EMAIL = os.environ.get('VAPID_CLAIMS_EMAIL', 'mailto:admin@stockvision.ai')


# ============================================
# VAPID Public Key Endpoint (for frontend)
# ============================================
@notifications_bp.route('/api/vapid-public-key')
def get_vapid_public_key():
    """Return the VAPID public key for push subscription"""
    if not VAPID_PUBLIC_KEY:
        return jsonify({
            'success': False,
            'error': 'VAPID keys not configured'
        }), 500
    
    return jsonify({
        'success': True,
        'publicKey': VAPID_PUBLIC_KEY
    })


# ============================================
# SMS Sending Endpoint
# ============================================
@notifications_bp.route('/api/sms/send', methods=['POST'])
@login_required
def send_sms():
    """
    Send an SMS alert via Twilio.
    
    Request JSON:
    {
        "message": "Your stock alert message"
    }
    
    Uses the phone number from the current user's profile.
    """
    try:
        # Check Twilio configuration
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
            return jsonify({
                'success': False,
                'error': 'Twilio credentials not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables.'
            }), 500
        
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        user = get_current_user()
        if not user.phone_number:
            return jsonify({
                'success': False,
                'error': 'No phone number on file. Please update your profile.'
            }), 400
        
        # Send SMS via Twilio
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        sms = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=user.phone_number
        )
        
        print(f"[SMS] Sent to {user.phone_number}: SID {sms.sid}")
        
        return jsonify({
            'success': True,
            'message': 'SMS sent successfully',
            'sid': sms.sid
        })
        
    except TwilioRestException as e:
        return jsonify({
            'success': False,
            'error': f'Twilio error: {str(e)}'
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# Push Subscription Management
# ============================================
@notifications_bp.route('/api/push/subscribe', methods=['POST'])
@login_required
def push_subscribe():
    """
    Store a push subscription for the current user.
    
    Request JSON:
    {
        "endpoint": "https://fcm.googleapis.com/...",
        "keys": {
            "p256dh": "...",
            "auth": "..."
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('endpoint') or not data.get('keys'):
            return jsonify({
                'success': False,
                'error': 'Invalid subscription data'
            }), 400
        
        user = get_current_user()
        endpoint = data['endpoint']
        keys = data['keys']
        
        # Check if subscription already exists
        existing = PushSubscription.query.filter_by(
            user_id=user.id,
            endpoint=endpoint
        ).first()
        
        if existing:
            # Update existing subscription
            existing.p256dh = keys['p256dh']
            existing.auth = keys['auth']
        else:
            # Create new subscription
            subscription = PushSubscription(
                user_id=user.id,
                endpoint=endpoint,
                p256dh=keys['p256dh'],
                auth=keys['auth']
            )
            db.session.add(subscription)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Push subscription saved'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notifications_bp.route('/api/push/unsubscribe', methods=['POST'])
@login_required
def push_unsubscribe():
    """Remove a push subscription"""
    try:
        data = request.get_json()
        endpoint = data.get('endpoint')
        
        if not endpoint:
            return jsonify({
                'success': False,
                'error': 'Endpoint is required'
            }), 400
        
        user = get_current_user()
        
        PushSubscription.query.filter_by(
            user_id=user.id,
            endpoint=endpoint
        ).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Unsubscribed from push notifications'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# Send Push Notification
# ============================================
@notifications_bp.route('/api/push/send', methods=['POST'])
@login_required
def send_push():
    """
    Send a push notification to the current user.
    
    Request JSON:
    {
        "title": "StockVision Alert",
        "body": "Your stock alert message",
        "url": "/dashboard"  # Optional: URL to open on click
    }
    """
    try:
        if not all([VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY]):
            return jsonify({
                'success': False,
                'error': 'VAPID keys not configured'
            }), 500
        
        data = request.get_json()
        title = data.get('title', 'StockVision Alert')
        body = data.get('body', '')
        url = data.get('url', '/dashboard')
        
        if not body:
            return jsonify({
                'success': False,
                'error': 'Body is required'
            }), 400
        
        user = get_current_user()
        subscriptions = PushSubscription.query.filter_by(user_id=user.id).all()
        
        if not subscriptions:
            return jsonify({
                'success': False,
                'error': 'No push subscriptions found. Please enable push notifications.'
            }), 400
        
        payload = json.dumps({
            'title': title,
            'body': body,
            'url': url
        })
        
        sent_count = 0
        errors = []
        
        for sub in subscriptions:
            try:
                webpush(
                    subscription_info=sub.to_dict(),
                    data=payload,
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims={'sub': VAPID_CLAIMS_EMAIL}
                )
                sent_count += 1
            except WebPushException as e:
                # Subscription might be expired; remove it
                if e.response and e.response.status_code in [404, 410]:
                    db.session.delete(sub)
                    db.session.commit()
                errors.append(str(e))
        
        return jsonify({
            'success': True,
            'sent': sent_count,
            'errors': errors if errors else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# Trigger Alert (Combined SMS + Push)
# ============================================
@notifications_bp.route('/api/alert/trigger', methods=['POST'])
@login_required
def trigger_alert():
    """
    Trigger an alert via both SMS and Push (if configured).
    
    Request JSON:
    {
        "message": "RELIANCE crossed above ₹3000!"
    }
    
    This endpoint attempts both notification methods and reports status for each.
    """
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        results = {
            'sms': {'sent': False, 'error': None},
            'push': {'sent': False, 'error': None}
        }
        
        user = get_current_user()
        
        # Attempt SMS
        if user.phone_number and all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
            try:
                client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                client.messages.create(
                    body=message,
                    from_=TWILIO_PHONE_NUMBER,
                    to=user.phone_number
                )
                results['sms']['sent'] = True
            except Exception as e:
                results['sms']['error'] = str(e)
        else:
            results['sms']['error'] = 'Not configured or no phone number'
        
        # Attempt Push
        if all([VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY]):
            subscriptions = PushSubscription.query.filter_by(user_id=user.id).all()
            if subscriptions:
                payload = json.dumps({
                    'title': 'StockVision Alert',
                    'body': message,
                    'url': '/dashboard'
                })
                for sub in subscriptions:
                    try:
                        webpush(
                            subscription_info=sub.to_dict(),
                            data=payload,
                            vapid_private_key=VAPID_PRIVATE_KEY,
                            vapid_claims={'sub': VAPID_CLAIMS_EMAIL}
                        )
                        results['push']['sent'] = True
                    except WebPushException as e:
                        if e.response and e.response.status_code in [404, 410]:
                            db.session.delete(sub)
                            db.session.commit()
                        results['push']['error'] = str(e)
            else:
                results['push']['error'] = 'No subscriptions'
        else:
            results['push']['error'] = 'VAPID not configured'
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
