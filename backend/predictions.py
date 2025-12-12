"""
StockVision - Predictions API Blueprint
Handles ML prediction requests and user prediction history
"""
from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json

from database import db
from models import User, Stock, Prediction, ActivityLog
from ml_service import generate_prediction, get_trend_label, get_confidence_label
from auth import login_required, get_current_user

# Create blueprint
predictions_bp = Blueprint('predictions', __name__)


# ============================================
# Run Prediction API
# ============================================
@predictions_bp.route('/api/predict', methods=['POST'])
@login_required
def run_prediction():
    """
    Run ML prediction for a stock.
    
    Request JSON:
    {
        "symbol": "RELIANCE.NS",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "model": "lstm",
        "horizon_days": 30
    }
    
    Response JSON:
    {
        "success": true,
        "prediction": {
            "symbol": "RELIANCE.NS",
            "model_used": "lstm",
            "historical": [...],
            "predicted": [...],
            "mae": 12.45,
            "rmse": 18.72,
            "confidence_level": 0.82,
            "trend": "bullish"
        }
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['symbol', 'start_date', 'end_date', 'model']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        symbol = data['symbol']
        start_date = data['start_date']
        end_date = data['end_date']
        model = data['model']
        horizon_days = data.get('horizon_days', 30)
        
        # Map frontend model names to backend
        model_mapping = {
            'linear': 'linear_regression',
            'lstm': 'lstm',
            'both': 'both'
        }
        model_used = model_mapping.get(model, model)
        
        # Validate dates
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_dt >= end_dt:
                return jsonify({
                    'success': False,
                    'error': 'Start date must be before end date'
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Get current user
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 401
        
        # Find or create stock
        # Clean symbol (remove .NS suffix for lookup)
        clean_symbol = symbol.replace('.NS', '').replace('.BSE', '').upper()
        stock = Stock.query.filter_by(symbol=clean_symbol).first()
        
        if not stock:
            # Create stock if not exists
            stock = Stock(
                symbol=clean_symbol,
                name=clean_symbol,
                exchange='NSE' if '.NS' in symbol else 'NASDAQ',
                sector='Unknown'
            )
            db.session.add(stock)
            db.session.commit()
        
        # Run prediction
        prediction_result = generate_prediction(
            symbol=symbol,  # Pass original symbol to preserve .NS suffix if present
            start_date=start_date,
            end_date=end_date,
            model_used=model_used,
            horizon_days=horizon_days
        )
        
        # Store prediction in database
        prediction = Prediction(
            user_id=user.id,
            stock_id=stock.id,
            model_used=model_used,
            start_date=start_dt.date(),
            end_date=end_dt.date(),
            horizon_days=horizon_days,
            mae=prediction_result['mae'],
            rmse=prediction_result['rmse'],
            confidence_level=prediction_result['confidence_level'],
            trend=prediction_result['trend'],
            raw_input_json=json.dumps(data),
            pred_json=json.dumps(prediction_result)
        )
        db.session.add(prediction)
        
        # Log activity
        log = ActivityLog(
            user_id=user.id,
            action='run_prediction',
            details=f'Ran {model_used} prediction for {clean_symbol}'
        )
        db.session.add(log)
        db.session.commit()
        
        # Add display-friendly labels to response
        prediction_result['trend_label'] = get_trend_label(prediction_result['trend'])
        prediction_result['confidence_label'] = get_confidence_label(prediction_result['confidence_level'])
        
        return jsonify({
            'success': True,
            'prediction': prediction_result,
            'prediction_id': prediction.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# Get User Predictions History
# ============================================
@predictions_bp.route('/api/user/predictions', methods=['GET'])
@login_required
def get_user_predictions():
    """
    Get paginated list of user's prediction history.
    
    Query params:
    - page: Page number (default 1)
    - per_page: Items per page (default 10, max 50)
    
    Response JSON:
    {
        "success": true,
        "predictions": [...],
        "total": 47,
        "page": 1,
        "per_page": 10,
        "pages": 5
    }
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 401
        
        # Pagination params
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        
        # Query predictions
        pagination = Prediction.query \
            .filter_by(user_id=user.id) \
            .order_by(Prediction.created_at.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)
        
        predictions = []
        for pred in pagination.items:
            predictions.append({
                'id': pred.id,
                'stock': pred.stock.to_dict() if pred.stock else None,
                'model_used': pred.model_used,
                'start_date': pred.start_date.isoformat() if pred.start_date else None,
                'end_date': pred.end_date.isoformat() if pred.end_date else None,
                'horizon_days': pred.horizon_days,
                'mae': pred.mae,
                'rmse': pred.rmse,
                'confidence_level': pred.confidence_level,
                'trend': pred.trend,
                'trend_label': get_trend_label(pred.trend),
                'confidence_label': get_confidence_label(pred.confidence_level),
                'created_at': pred.created_at.isoformat() if pred.created_at else None
            })
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# Get Single Prediction
# ============================================
@predictions_bp.route('/api/prediction/<int:prediction_id>', methods=['GET'])
@login_required
def get_prediction(prediction_id):
    """
    Get a single prediction by ID.
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 401
        
        prediction = Prediction.query.get(prediction_id)
        
        if not prediction:
            return jsonify({
                'success': False,
                'error': 'Prediction not found'
            }), 404
        
        # Check ownership (unless admin)
        if prediction.user_id != user.id and not user.is_admin():
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Parse stored JSON
        result = prediction.to_dict()
        if prediction.pred_json:
            result['prediction_data'] = json.loads(prediction.pred_json)
        
        return jsonify({
            'success': True,
            'prediction': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# Get Available Stocks
# ============================================
@predictions_bp.route('/api/stocks', methods=['GET'])
def get_stocks():
    """
    Get list of available stocks for the dropdown.
    """
    try:
        stocks = Stock.query.order_by(Stock.symbol).all()
        
        # Group by sector
        by_sector = {}
        for stock in stocks:
            sector = stock.sector or 'Other'
            if sector not in by_sector:
                by_sector[sector] = []
            by_sector[sector].append(stock.to_dict())
        
        return jsonify({
            'success': True,
            'stocks': [s.to_dict() for s in stocks],
            'by_sector': by_sector
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
