"""
StockVision - Database Setup
SQLAlchemy configuration and initialization
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()


def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Import models to ensure they are registered
        from models import User, Stock, Prediction, ActivityLog
        
        # Create all tables
        db.create_all()
        
        # Seed initial data if database is empty
        seed_initial_data()


def seed_initial_data():
    """Seed the database with initial data"""
    from models import User, Stock
    from werkzeug.security import generate_password_hash
    
    # Check if admin user exists
    if not User.query.filter_by(email='admin@stockvision.com').first():
        # Create admin user
        admin = User(
            name='Admin User',
            email='admin@stockvision.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        
        # Create demo user
        demo_user = User(
            name='Demo User',
            email='user@stockvision.com',
            password_hash=generate_password_hash('user123'),
            role='user',
            is_active=True
        )
        db.session.add(demo_user)
        
        print("[SUCCESS] Created admin and demo users")
    
    # Check if stocks exist
    if not Stock.query.first():
        # Initial stocks matching the frontend dropdown
        stocks_data = [
            # Indian Stocks - IT & Tech
            {'symbol': 'TCS', 'name': 'Tata Consultancy', 'exchange': 'NSE', 'sector': 'IT'},
            {'symbol': 'INFY', 'name': 'Infosys', 'exchange': 'NSE', 'sector': 'IT'},
            {'symbol': 'WIPRO', 'name': 'Wipro', 'exchange': 'NSE', 'sector': 'IT'},
            {'symbol': 'HCLTECH', 'name': 'HCL Technologies', 'exchange': 'NSE', 'sector': 'IT'},
            {'symbol': 'TECHM', 'name': 'Tech Mahindra', 'exchange': 'NSE', 'sector': 'IT'},
            
            # Indian Stocks - Banking & Finance
            {'symbol': 'HDFCBANK', 'name': 'HDFC Bank', 'exchange': 'NSE', 'sector': 'Banking'},
            {'symbol': 'ICICIBANK', 'name': 'ICICI Bank', 'exchange': 'NSE', 'sector': 'Banking'},
            {'symbol': 'SBIN', 'name': 'State Bank of India', 'exchange': 'NSE', 'sector': 'Banking'},
            {'symbol': 'KOTAKBANK', 'name': 'Kotak Mahindra Bank', 'exchange': 'NSE', 'sector': 'Banking'},
            {'symbol': 'AXISBANK', 'name': 'Axis Bank', 'exchange': 'NSE', 'sector': 'Banking'},
            {'symbol': 'BAJFINANCE', 'name': 'Bajaj Finance', 'exchange': 'NSE', 'sector': 'Finance'},
            
            # Indian Stocks - Energy & Infrastructure
            {'symbol': 'RELIANCE', 'name': 'Reliance Industries', 'exchange': 'NSE', 'sector': 'Energy'},
            {'symbol': 'POWERGRID', 'name': 'Power Grid Corp', 'exchange': 'NSE', 'sector': 'Energy'},
            {'symbol': 'NTPC', 'name': 'NTPC Limited', 'exchange': 'NSE', 'sector': 'Energy'},
            {'symbol': 'ONGC', 'name': 'Oil & Natural Gas Corp', 'exchange': 'NSE', 'sector': 'Energy'},
            {'symbol': 'LT', 'name': 'Larsen & Toubro', 'exchange': 'NSE', 'sector': 'Infrastructure'},
            {'symbol': 'ADANIENT', 'name': 'Adani Enterprises', 'exchange': 'NSE', 'sector': 'Conglomerate'},
            
            # Indian Stocks - Consumer & Retail
            {'symbol': 'HINDUNILVR', 'name': 'Hindustan Unilever', 'exchange': 'NSE', 'sector': 'Consumer'},
            {'symbol': 'ITC', 'name': 'ITC Limited', 'exchange': 'NSE', 'sector': 'Consumer'},
            {'symbol': 'TITAN', 'name': 'Titan Company', 'exchange': 'NSE', 'sector': 'Consumer'},
            {'symbol': 'ASIANPAINT', 'name': 'Asian Paints', 'exchange': 'NSE', 'sector': 'Consumer'},
            
            # Indian Stocks - Auto & Telecom
            {'symbol': 'MARUTI', 'name': 'Maruti Suzuki', 'exchange': 'NSE', 'sector': 'Auto'},
            {'symbol': 'TATAMOTORS', 'name': 'Tata Motors', 'exchange': 'NSE', 'sector': 'Auto'},
            {'symbol': 'BHARTIARTL', 'name': 'Bharti Airtel', 'exchange': 'NSE', 'sector': 'Telecom'},
            
            # Indian Stocks - Pharma & Healthcare
            {'symbol': 'SUNPHARMA', 'name': 'Sun Pharmaceutical', 'exchange': 'NSE', 'sector': 'Pharma'},
            {'symbol': 'DRREDDY', 'name': "Dr. Reddy's Labs", 'exchange': 'NSE', 'sector': 'Pharma'},
            {'symbol': 'CIPLA', 'name': 'Cipla', 'exchange': 'NSE', 'sector': 'Pharma'},
            
            # US Stocks - Tech Giants
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'exchange': 'NASDAQ', 'sector': 'Technology'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'exchange': 'NASDAQ', 'sector': 'Technology'},
            {'symbol': 'MSFT', 'name': 'Microsoft', 'exchange': 'NASDAQ', 'sector': 'Technology'},
            {'symbol': 'AMZN', 'name': 'Amazon', 'exchange': 'NASDAQ', 'sector': 'Technology'},
            {'symbol': 'META', 'name': 'Meta Platforms', 'exchange': 'NASDAQ', 'sector': 'Technology'},
            {'symbol': 'NVDA', 'name': 'NVIDIA', 'exchange': 'NASDAQ', 'sector': 'Technology'},
            {'symbol': 'TSLA', 'name': 'Tesla', 'exchange': 'NASDAQ', 'sector': 'Auto'},
            {'symbol': 'NFLX', 'name': 'Netflix', 'exchange': 'NASDAQ', 'sector': 'Entertainment'},
            
            # US Stocks - Finance
            {'symbol': 'JPM', 'name': 'JPMorgan Chase', 'exchange': 'NYSE', 'sector': 'Banking'},
            {'symbol': 'V', 'name': 'Visa', 'exchange': 'NYSE', 'sector': 'Finance'},
            {'symbol': 'PYPL', 'name': 'PayPal', 'exchange': 'NASDAQ', 'sector': 'Finance'},
            
            # US Stocks - Consumer
            {'symbol': 'WMT', 'name': 'Walmart', 'exchange': 'NYSE', 'sector': 'Retail'},
            {'symbol': 'PG', 'name': 'Procter & Gamble', 'exchange': 'NYSE', 'sector': 'Consumer'},
            {'symbol': 'DIS', 'name': 'Walt Disney', 'exchange': 'NYSE', 'sector': 'Entertainment'},
            {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'exchange': 'NYSE', 'sector': 'Healthcare'},
        ]
        
        for stock_data in stocks_data:
            stock = Stock(**stock_data)
            db.session.add(stock)
        
        print(f"[SUCCESS] Created {len(stocks_data)} stocks")
    
    db.session.commit()
