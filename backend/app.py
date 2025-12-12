"""
StockVision - Main Application Entry Point
"""
from flask import Flask, render_template, send_from_directory, jsonify
from config import config
from database import init_db
import os

# Create Flask app
def create_app(config_name='default'):
    app = Flask(__name__, static_folder='../assets', static_url_path='/static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    from auth import auth_bp
    from predictions import predictions_bp
    from dashboards import dashboards_bp
    from notifications import notifications_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(dashboards_bp)
    app.register_blueprint(notifications_bp)
    
    # Main/Landing Routes
    @app.route('/')
    def landing():
        return render_template('landing.html')
    
    @app.route('/about.html')
    def about():
        # Map legacy .html URLs to routes if needed, or serve template
        return render_template('landing.html')  # For now redirect to landing or create specific page
    
    @app.route('/contact.html')
    def contact():
        return render_template('landing.html')  # Placeholder
        
    @app.route('/faq')
    def faq():
        return render_template('faq.html')
    
    # Serve Service Worker from root (required for push notifications scope)
    @app.route('/sw.js')
    def service_worker():
        return send_from_directory(app.static_folder + '/js', 'sw.js', mimetype='application/javascript')
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error_code=404, message="Page not found"), 404
        
    @app.errorhandler(500)
    @app.errorhandler(500)
    def internal_server_error(e):
        import traceback
        # In production, we usually hide this, but for this specific debugging session we expose it.
        return render_template('error.html', 
            error_code=500, 
            message="Internal server error",
            detail=traceback.format_exc()
        ), 500
    
    return app

# Check if run directly
if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    app.run()
