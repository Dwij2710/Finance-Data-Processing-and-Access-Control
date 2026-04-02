# Finance Dashboard API

A role-aware REST backend for a finance dashboard system, built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Database | SQLite (file: `finance.db`) |
| Auth | JWT (via `python-jose`) |
| Validation | Pydantic v2 |
| Password Hashing | bcrypt (via `passlib`) |

---

## Project Structure

```
finance-backend/
├── app/
│   ├── main.py               # App entry point, router registration
│   ├── database.py           # DB engine, session, Base
│   ├── core/
│   │   ├── config.py         # Settings from .env
│   │   ├── security.py       # JWT + password hashing
│   │   └── dependencies.py   # get_current_user, require_roles guard
│   ├── models/
│   │   ├── user.py           # User model + UserRole enum
│   │   └── financial.py      # FinancialRecord model + RecordType enum
│   ├── schemas/
│   │   ├── user.py           # Pydantic schemas for user endpoints
│   │   ├── financial.py      # Pydantic schemas for record endpoints
│   │   └── dashboard.py      # Pydantic schemas for dashboard endpoints
│   ├── routers/
│   │   ├── auth.py           # POST /auth/register, POST /auth/login
│   │   ├── users.py          # User management (Admin only)
│   │   ├── financial.py      # Financial record CRUD + filters
│   │   └── dashboard.py      # Dashboard analytics endpoints
│   └── services/
│       ├── user_service.py       # User business logic
│       ├── financial_service.py  # Record CRUD + filtering logic
│       └── dashboard_service.py  # Aggregation queries
├── seed.py                   # Seed script (sample users + records)
├── requirements.txt
├── .env
└── README.md
```

---

## Getting Started

### 1. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment (optional)

The `.env` file is pre-configured with defaults. For production, change `SECRET_KEY`.

```env
SECRET_KEY=your-production-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./finance.db
```

### 4. Start the server

```bash
uvicorn app.main:app --reload
```

Server starts at: **http://localhost:8000**

### 5. Seed sample data

```bash
python seed.py
```

---

## API Documentation

Visit **http://localhost:8000/docs** for the interactive Swagger UI.

---

## Authentication Flow

1. **Register** a user via `POST /auth/register`
2. **Login** via `POST /auth/login` — receives a JWT token
3. Click **Authorize** in Swagger UI, enter: `Bearer <token>`
4. All protected endpoints are now accessible

---

## Role-Based Access Control

| Endpoint Group | Viewer | Analyst | Admin |
|---|---|---|---|
| `GET /records/` | ✅ | ✅ | ✅ |
| `GET /records/{id}` | ✅ | ✅ | ✅ |
| `GET /dashboard/recent` | ✅ | ✅ | ✅ |
| `GET /dashboard/summary` | ❌ | ✅ | ✅ |
| `GET /dashboard/categories` | ❌ | ✅ | ✅ |
| `GET /dashboard/trends` | ❌ | ✅ | ✅ |
| `POST /records/` | ❌ | ✅ | ✅ |
| `PUT /records/{id}` | ❌ | ❌ | ✅ |
| `DELETE /records/{id}` | ❌ | ❌ | ✅ |
| `GET /users/` | ❌ | ❌ | ✅ |
| `PUT /users/{id}/role` | ❌ | ❌ | ✅ |
| `PUT /users/{id}/status` | ❌ | ❌ | ✅ |
| `DELETE /users/{id}` | ❌ | ❌ | ✅ |

---

## API Endpoints Reference

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, returns JWT token |

### Users (Admin only)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/users/me` | Get your own profile |
| GET | `/users/` | List all users |
| GET | `/users/{id}` | Get user by ID |
| PUT | `/users/{id}/role` | Change user role |
| PUT | `/users/{id}/status` | Activate/deactivate user |
| DELETE | `/users/{id}` | Delete user |

### Financial Records
| Method | Endpoint | Description |
|---|---|---|
| POST | `/records/` | Create record |
| GET | `/records/` | List records (filterable) |
| GET | `/records/{id}` | Get single record |
| PUT | `/records/{id}` | Update record (Admin) |
| DELETE | `/records/{id}` | Delete record (Admin) |

**Record Filters** (query params on `GET /records/`):
- `?type=income` or `?type=expense`
- `?category=Rent` (partial match)
- `?from_date=2025-01-01&to_date=2025-12-31`
- `?skip=0&limit=50`

### Dashboard
| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard/summary` | Total income, expenses, net balance |
| GET | `/dashboard/categories` | Totals by category + type |
| GET | `/dashboard/trends` | Monthly income/expense trends |
| GET | `/dashboard/recent` | Last N transactions |

---

## Test Credentials (after seeding)

| Role | Email | Password |
|---|---|---|
| Admin | admin@finance.com | admin123 |
| Analyst | analyst@finance.com | analyst123 |
| Viewer | viewer@finance.com | viewer123 |

---

## Data Persistence Note

This project uses **SQLite** stored in `finance.db` in the project root.
This requires zero configuration and is suitable for development and evaluation.
To switch to PostgreSQL, update `DATABASE_URL` in `.env` and remove the `check_same_thread` SQLite argument in `database.py`.

---

## Error Handling

| Status | Meaning |
|---|---|
| 400 | Bad request / invalid operation |
| 401 | Missing or invalid JWT token |
| 403 | Authenticated but insufficient role |
| 404 | Resource not found |
| 409 | Conflict (e.g., duplicate email) |
| 422 | Validation error (Pydantic) |
| 500 | Unexpected server error |
