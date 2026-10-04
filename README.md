# FinTrack - Personal Finance Analyzer

A scalable, production-ready backend API for a personal finance tracker, built with FastAPI and MongoDB (Motor).

## Features
- **Authentication**: JWT-based login and registration.
- **RBAC**: Role-Based Access Control (Free, Premium, Admin, etc.).
- **Transactions**: Add income and expenses.
- **Categories**: Automatic simple rule-based categorization.
- **Budgets**: Set and track monthly budgets.
- **Goals**: Create and contribute to savings goals.
- **Analytics**: Overview of income, expenses, and savings rate.

## Technology Stack
- Python 3.10+
- FastAPI
- MongoDB (Motor async driver)
- Pydantic
- JWT (python-jose)
- Passlib (bcrypt)
- Pytest

## Project Structure
```
app/
├── api/          # FastAPI routers
├── core/         # Config, security, exceptions, permissions
├── database/     # MongoDB connection and indexes
├── schemas/      # Pydantic validation models
└── main.py       # Application entry point
tests/            # Pytest suite
```

## Setup & Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=fintrack_db
   JWT_SECRET_KEY=your-secret-key
   ```
4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation
Once the server is running, visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
