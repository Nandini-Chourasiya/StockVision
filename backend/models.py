"""
StockVision - Database Models
SQLAlchemy ORM models for Users, Stocks, Predictions, and Activity Logs
"""
from datetime import datetime
from database import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """User model for authentication and tracking"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'user' or 'admin'
    is_active = db.Column(db.Boolean, default=True)
    phone_number = db.Column(db.String(20))  # For SMS alerts (E.164 format)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy='dynamic')
    push_subscriptions = db.relationship('PushSubscription', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
    
    def to_dict(self):
        """Convert user to dictionary (excluding password)"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Stock(db.Model):
    """Stock model for available trading symbols"""
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    exchange = db.Column(db.String(20), nullable=False)  # NSE, NYSE, NASDAQ
    sector = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='stock', lazy='dynamic')
    
    def __repr__(self):
        return f'<Stock {self.symbol}>'
    
    def to_dict(self):
        """Convert stock to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'exchange': self.exchange,
            'sector': self.sector
        }


class Prediction(db.Model):
    """Prediction model for storing ML prediction results"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False, index=True)
    
    # Model configuration
    model_used = db.Column(db.String(20), nullable=False)  # 'linear_regression' or 'lstm'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    horizon_days = db.Column(db.Integer, default=30)
    
    # Metrics
    mae = db.Column(db.Float)  # Mean Absolute Error
    rmse = db.Column(db.Float)  # Root Mean Squared Error
    confidence_level = db.Column(db.Float)  # 0.0 to 1.0
    trend = db.Column(db.String(20))  # 'bullish', 'bearish', 'sideways'
    
    # JSON data
    raw_input_json = db.Column(db.Text)  # Original input parameters
    pred_json = db.Column(db.Text)  # Prediction results for charting
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Prediction {self.id} - {self.model_used}>'
    
    def to_dict(self):
        """Convert prediction to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'stock': self.stock.to_dict() if self.stock else None,
            'model_used': self.model_used,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'horizon_days': self.horizon_days,
            'mae': self.mae,
            'rmse': self.rmse,
            'confidence_level': self.confidence_level,
            'trend': self.trend,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ActivityLog(db.Model):
    """Activity log for tracking user actions"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False)  # 'login', 'logout', 'run_prediction', etc.
    details = db.Column(db.Text)  # Additional context
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<ActivityLog {self.action} by User {self.user_id}>'
    
    def to_dict(self):
        """Convert activity log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'action': self.action,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PushSubscription(db.Model):
    """Push subscription model for Web Push notifications"""
    __tablename__ = 'push_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    endpoint = db.Column(db.Text, nullable=False)  # Push service endpoint URL
    p256dh = db.Column(db.String(256), nullable=False)  # Public key
    auth = db.Column(db.String(64), nullable=False)  # Auth secret
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PushSubscription {self.id} for User {self.user_id}>'
    
    def to_dict(self):
        """Convert subscription to dictionary for pywebpush"""
        return {
            'endpoint': self.endpoint,
            'keys': {
                'p256dh': self.p256dh,
                'auth': self.auth
            }
        }
