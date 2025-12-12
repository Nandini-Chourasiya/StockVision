# StockVision - Stock Price Predictor Platform (Backend)

Fully functional Flask backend for StockVision, enabling user authentication, stock price predictions using ML models (Linear Regression & LSTM), and admin management.

## Features

- **Authentication**: Secure login/registration with hashed passwords and session management.
- **Role-Based Access**: Separate dashboards for Users and Admins.
- **ML Predictions**:
  - **Linear Regression**: Trend detection.
  - **LSTM (Mock)**: Complex pattern recognition demo.
  - **Metrics**: MAE, RMSE, Confidence Level, and Trend Analysis.
- **Interactive Dashboards**:
  - **User**: Run predictions, view history, and interactive charts (Chart.js).
  - **Admin**: Platform stats, user management, and activity logs.
- **REST APIs**: Endpoints for predictions and management.

## Project Structure

```
backend/
├── app.py              # Main application entry point
├── config.py           # Configuration settings
├── database.py         # Database setup and seed data
├── models.py           # SQLAlchemy database models
├── auth.py             # Authentication blueprint
├── ml_service.py       # ML Pipeline (Data Collection -> Prediction -> Vis)
├── predictions.py      # Prediction API blueprint
├── dashboards.py       # Dashboard routes
├── schema.sql          # SQL schema reference
└── templates/          # Jinja2 templates (matches frontend design)
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. **Navigate to the backend directory:**
   ```bash
   cd "backend"
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Flask server:**
   ```bash
   flask run
   ```

2. **Access the application:**
   Open your browser and go to `http://127.0.0.1:5000/`.

### Initial Credentials

The database is automatically seeded with these demo accounts:

**Admin Account:**
- **Email:** `admin@stockvision.com`
- **Password:** `admin123`

**User Account:**
- **Email:** `user@stockvision.com`
- **Password:** `user123`

## Development Notes

- **Database:** Uses SQLite (`stockvision.db`). Created automatically on first run.
- **ML Models:** Uses synthetic data generation for demonstration purposes as per requirement.
- **Frontend Assets:** The backend is configured to serve static assets (CSS/JS) from the `../assets` directory relative to `backend/`.

## License

Educational use only. Not for real trading.
