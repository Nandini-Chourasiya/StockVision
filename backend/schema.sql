-- StockVision Database Schema Reference

-- Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_users_email ON users (email);

-- Stocks Table
CREATE TABLE stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    sector VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_stocks_symbol ON stocks (symbol);

-- Predictions Table
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    model_used VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    horizon_days INTEGER DEFAULT 30,
    mae FLOAT,
    rmse FLOAT,
    confidence_level FLOAT,
    trend VARCHAR(20),
    raw_input_json TEXT,
    pred_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(stock_id) REFERENCES stocks(id)
);

CREATE INDEX ix_predictions_user_id ON predictions (user_id);
CREATE INDEX ix_predictions_stock_id ON predictions (stock_id);
CREATE INDEX ix_predictions_created_at ON predictions (created_at);

-- Activity Logs Table
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE INDEX ix_activity_logs_user_id ON activity_logs (user_id);
CREATE INDEX ix_activity_logs_created_at ON activity_logs (created_at);
