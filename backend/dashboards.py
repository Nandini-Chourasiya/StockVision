"""
StockVision - Dashboards Blueprint
User and Admin dashboard routes with statistics APIs
"""
from flask import Blueprint, render_template, request, jsonify, session
from sqlalchemy import func
from datetime import datetime, timedelta

from database import db
from models import User, Stock, Prediction, ActivityLog
from auth import login_required, admin_required, get_current_user
from ml_service import get_trend_label, get_confidence_label

# Create blueprint
dashboards_bp = Blueprint('dashboards', __name__)


# ============================================
# User Dashboard
# ============================================
@dashboards_bp.route('/dashboard')
@login_required
def user_dashboard():
    """User dashboard page"""
    try:
        user = get_current_user()
        
        # Get user statistics
        total_predictions = Prediction.query.filter_by(user_id=user.id).count()
        
        # Get last prediction
        last_prediction = Prediction.query \
            .filter_by(user_id=user.id) \
            .order_by(Prediction.created_at.desc()) \
            .first()
        
        last_stock = last_prediction.stock.symbol if last_prediction and last_prediction.stock else 'N/A'
        
        # Get recent predictions for table
        recent_predictions = Prediction.query \
            .filter_by(user_id=user.id) \
            .order_by(Prediction.created_at.desc()) \
            .limit(10) \
            .all()
        
        # Calculate average confidence
        avg_confidence = db.session.query(func.avg(Prediction.confidence_level)) \
            .filter_by(user_id=user.id) \
            .scalar()
        
        if avg_confidence:
            avg_confidence_label = get_confidence_label(avg_confidence)
        else:
            avg_confidence_label = 'N/A'
        
        # Get all stocks for dropdown
        stocks = Stock.query.order_by(Stock.symbol).all()
        
        # Group stocks by sector for dropdown
        stocks_by_sector = {}
        for stock in stocks:
            sector = stock.sector or 'Other'
            if sector not in stocks_by_sector:
                stocks_by_sector[sector] = []
            stocks_by_sector[sector].append(stock)
        
        return render_template('user_dashboard.html',
            user=user,
            total_predictions=total_predictions,
            last_prediction=last_prediction,
            last_stock=last_stock,
            avg_confidence_label=avg_confidence_label,
            recent_predictions=recent_predictions,
            stocks=stocks,
            stocks_by_sector=stocks_by_sector,
            get_trend_label=get_trend_label,
            get_confidence_label=get_confidence_label
        )
    except Exception as e:
        import traceback
        return render_template('error.html', 
            error_code=500, 
            message=f"Dashboard Error: {str(e)}",
            detail=traceback.format_exc()
        ), 500


# ============================================
# User Statistics API
# ============================================
@dashboards_bp.route('/api/user/stats')
@login_required
def user_stats():
    """
    Get current user statistics for dashboard updates.
    """
    try:
        user = get_current_user()
        
        # Total predictions
        total_predictions = Prediction.query.filter_by(user_id=user.id).count()
        
        # Last prediction stock
        last_prediction = Prediction.query \
            .filter_by(user_id=user.id) \
            .order_by(Prediction.created_at.desc()) \
            .first()
        
        last_stock = last_prediction.stock.symbol if last_prediction and last_prediction.stock else 'N/A'
        
        # Average confidence
        avg_confidence = db.session.query(func.avg(Prediction.confidence_level)) \
            .filter_by(user_id=user.id) \
            .scalar()
        
        if avg_confidence:
            avg_confidence_label = get_confidence_label(avg_confidence)
        else:
            avg_confidence_label = 'N/A'
            
        return jsonify({
            'success': True,
            'total_predictions': total_predictions,
            'last_stock': last_stock,
            'avg_confidence_label': avg_confidence_label
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



# ============================================
# Admin Dashboard
# ============================================
@dashboards_bp.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard page"""
    user = get_current_user()
    
    # Platform statistics
    total_users = User.query.count()
    total_predictions = Prediction.query.count()
    
    # Most used stock
    most_used_stock_result = db.session.query(
        Stock.symbol,
        func.count(Prediction.id).label('count')
    ).join(Prediction).group_by(Stock.id).order_by(func.count(Prediction.id).desc()).first()
    
    most_used_stock = most_used_stock_result[0] if most_used_stock_result else 'N/A'
    
    # 24h activity count
    yesterday = datetime.utcnow() - timedelta(hours=24)
    activity_24h = ActivityLog.query.filter(ActivityLog.created_at >= yesterday).count()
    
    # Get all users for management table
    users = User.query.order_by(User.created_at.desc()).all()
    
    # Recent activity logs
    recent_activity = ActivityLog.query \
        .order_by(ActivityLog.created_at.desc()) \
        .limit(20) \
        .all()
    
    # Predictions per day (last 7 days)
    predictions_by_day = []
    for i in range(6, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        count = Prediction.query.filter(
            func.date(Prediction.created_at) == day
        ).count()
        predictions_by_day.append({
            'date': day.strftime('%b %d'),
            'count': count
        })
    
    # Model usage distribution
    model_usage = db.session.query(
        Prediction.model_used,
        func.count(Prediction.id).label('count')
    ).group_by(Prediction.model_used).all()
    
    model_usage_data = {m[0]: m[1] for m in model_usage}
    
    # User signups over time (last 30 days)
    signups_by_day = []
    for i in range(29, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        count = User.query.filter(
            func.date(User.created_at) == day
        ).count()
        signups_by_day.append({
            'date': day.strftime('%b %d'),
            'count': count
        })
    
    return render_template('admin_dashboard.html',
        user=user,
        total_users=total_users,
        total_predictions=total_predictions,
        most_used_stock=most_used_stock,
        activity_24h=activity_24h,
        users=users,
        recent_activity=recent_activity,
        predictions_by_day=predictions_by_day,
        model_usage_data=model_usage_data,
        signups_by_day=signups_by_day
    )


# ============================================
# Admin Statistics API
# ============================================
@dashboards_bp.route('/api/admin/stats')
@admin_required
def admin_stats():
    """
    Get platform statistics for admin dashboard.
    
    Response JSON:
    {
        "success": true,
        "total_users": 156,
        "total_predictions": 1247,
        "most_used_stock": "RELIANCE",
        "most_used_model": "linear_regression",
        "recent_activity": [...]
    }
    """
    try:
        # Total users
        total_users = User.query.count()
        
        # Total predictions
        total_predictions = Prediction.query.count()
        
        # Most used stock
        most_used_stock_result = db.session.query(
            Stock.symbol,
            func.count(Prediction.id).label('count')
        ).join(Prediction).group_by(Stock.id).order_by(func.count(Prediction.id).desc()).first()
        
        most_used_stock = most_used_stock_result[0] if most_used_stock_result else 'N/A'
        
        # Most used model
        most_used_model_result = db.session.query(
            Prediction.model_used,
            func.count(Prediction.id).label('count')
        ).group_by(Prediction.model_used).order_by(func.count(Prediction.id).desc()).first()
        
        most_used_model = most_used_model_result[0] if most_used_model_result else 'N/A'
        
        # Recent activity
        recent_activity = ActivityLog.query \
            .order_by(ActivityLog.created_at.desc()) \
            .limit(10) \
            .all()
        
        return jsonify({
            'success': True,
            'total_users': total_users,
            'total_predictions': total_predictions,
            'most_used_stock': most_used_stock,
            'most_used_model': most_used_model,
            'recent_activity': [log.to_dict() for log in recent_activity]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# Admin User Management API
# ============================================
@dashboards_bp.route('/api/admin/user/role', methods=['POST'])
@admin_required
def change_user_role():
    """
    Change user role or status.
    
    Request JSON:
    {
        "user_id": 2,
        "action": "change_role",  # or "activate", "deactivate"
        "role": "admin"  # optional, for change_role action
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        user_id = data.get('user_id')
        action = data.get('action')
        
        if not user_id or not action:
            return jsonify({
                'success': False,
                'error': 'user_id and action are required'
            }), 400
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        current_admin = get_current_user()
        
        # Prevent admin from modifying their own role
        if user.id == current_admin.id:
            return jsonify({
                'success': False,
                'error': 'Cannot modify your own account'
            }), 400
        
        if action == 'change_role':
            new_role = data.get('role', 'user')
            if new_role not in ['user', 'admin']:
                return jsonify({
                    'success': False,
                    'error': 'Invalid role'
                }), 400
            
            user.role = new_role
            message = f"Changed {user.name}'s role to {new_role}"
            
        elif action == 'activate':
            user.is_active = True
            message = f"Activated {user.name}'s account"
            
        elif action == 'deactivate':
            user.is_active = False
            message = f"Deactivated {user.name}'s account"
            
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid action'
            }), 400
        
        # Log activity
        log = ActivityLog(
            user_id=current_admin.id,
            action='admin_user_update',
            details=message
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# Get Users List (Admin)
# ============================================
@dashboards_bp.route('/api/admin/users')
@admin_required
def get_users():
    """Get all users for admin management."""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
