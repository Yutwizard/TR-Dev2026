# Treasury Management System - Backend Application

## Structure

```
src/backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry
│   ├── config.py            # Configuration settings
│   │
│   ├── core/                # Core utilities
│   │   ├── __init__.py
│   │   ├── auth.py          # JWT authentication
│   │   ├── security.py      # Password hashing, security utils
│   │   ├── permissions.py   # Role-based access control
│   │   └── exceptions.py    # Custom exceptions
│   │
│   ├── services/            # Business logic services
│   │   ├── __init__.py
│   │   ├── calendar_service.py     # Thai business day calendar
│   │   ├── settlement_service.py   # BAHTNET/TSD message generation
│   │   └── ...
│   │
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── ...
│   │
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   └── ...
│   │
│   ├── routers/             # API routes
│   │   ├── __init__.py
│   │   └── ...
│   │
│   └── tests/               # Unit tests
│       ├── __init__.py
│       └── ...
│
├── alembic/                 # Database migrations
├── scripts/                 # Utility scripts
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Quick Start

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

## API Documentation

When running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
