# FinTrack - Personal Finance Analyzer

FinTrack is a comprehensive, full-stack Personal Finance Analyzer designed to give users granular control over their transactions, budgets, goals, and analytics, powered by a scalable FastAPI backend and a modern React Vite frontend.

## Architecture
- **Backend:** FastAPI, Python, MongoDB Atlas (Motor Async driver), PyJWT (Authentication)
- **Frontend:** React, Vite, TypeScript, Axios, React Router v6
- **Database:** MongoDB Atlas (No localhost required)

## Features & RBAC
- **Authentication:** JWT Access & Refresh token rotation, Bcrypt password hashing.
- **Transactions:** Full CRUD with category mapping and smart anomaly detection.
- **Budgets & Goals:** Progress tracking, usage calculation, and goal threshold notifications.
- **Analytics:** High-performance MongoDB aggregations for Savings, Overviews, and Categorization.
- **Roles:** Super Admin, Admin, Financial Advisor, Premium User, Free User, Auditor. (Full backend enforcement).

## Setup & Execution

### Environment Setup (`.env`)
Create a `.env` in the root:
```env
MONGODB_URL=mongodb+srv://<user>:<password>@cluster.mongodb.net/
DATABASE_NAME=fintrack
JWT_SECRET_KEY=your_secure_secret_here
```

### Backend Installation
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Installation
```bash
cd frontend
npm install
npm run dev
```

## Testing
To run the automated Pytest suites (isolated via `mongomock`):
```bash
pytest -v
```

## Security
This project uses strictly isolated JWT refresh tokens and MongoDB aggregations. No secrets, passwords, or `.env` files are pushed to this repository. All passwords are conservatively hashed with `bcrypt`.

---
*Developed autonomously via Google Antigravity.*
