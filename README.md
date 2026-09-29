# Secure User Authentication & Signup Portal

A modern, full-stack user registration and authentication web application built with **FastAPI**, **SQLite** (via SQLAlchemy), **Bcrypt** password hashing, **JWT** session tokens, and a responsive frontend with real-time form validation.

---

## ✨ Features

- **Backend**:
  - **FastAPI**: Async, typed, high-performance REST API with automated OpenAPI / Swagger documentation (`/docs`).
  - **SQLite Database**: Relational storage via SQLAlchemy ORM with automatic schema migration on startup.
  - **Security Best Practices**:
    - Passwords securely hashed with **Bcrypt** (12 salt rounds, one-way hash).
    - **JWT (JSON Web Token)** authentication (`Bearer` tokens with 24-hour expiration).
    - Case-insensitive unique username and email constraints.
  - **Input Validation**: Pydantic schemas validating email format, username restrictions, and password strength policies.

- **Frontend**:
  - **Dual Mode Views**: Seamless tabbed navigation between **Create Account** and **Sign In**.
  - **Live Password Strength Meter**: 5-point evaluation (length, uppercase, lowercase, numbers, special characters) with real-time animated visual bar and checklist.
  - **Real-Time Validation**: Instant feedback for email format, username validity, and matching confirm-password.
  - **User Dashboard & Database Viewer**:
    - Welcome hero screen displaying profile metadata and active session details.
    - Live SQLite user registry showing accounts currently persisted in the database.
    - Sign out functionality clearing local credentials.

---

## 📁 Project Structure

```
├── backend/
│   ├── __init__.py
│   ├── auth.py          # Bcrypt hashing, JWT issuance & token verification
│   ├── database.py      # SQLite connection & SQLAlchemy session management
│   ├── models.py        # Database models (User entity)
│   ├── schemas.py       # Pydantic validation models (UserCreate, UserLogin, UserResponse)
│   └── main.py          # FastAPI application, route handlers & static file serving
├── frontend/
│   ├── index.html       # Web portal markup (Signup, Login, Dashboard)
│   ├── css/
│   │   └── style.css    # Responsive styles, dark mode UI, password meter
│   └── js/
│       └── app.js       # Client validation, API requests, session handling
├── tests/
│   ├── __init__.py
│   └── test_auth.py     # Automated test suite (Signup, Login, Hashing, In-memory DB)
├── requirements.txt     # Python package dependencies
├── pytest.ini          # Test runner configuration
├── run.py               # Application entrypoint script
└── README.md
```

---

## 🚀 Quickstart

### 1. Activate Virtual Environment

- **Bash / Zsh**:
  ```bash
  source .venv/bin/activate
  ```
- **Fish Shell**:
  ```fish
  source .venv/bin/activate.fish
  ```

*(Or simply run scripts directly without activation using `./.venv/bin/python`)*

### 2. Start the Server

```bash
# If activated:
python3 run.py

# Or directly without activating:
./.venv/bin/python3 run.py
```

Or using `uvicorn` directly:
```bash
uvicorn backend.main:app --reload --port 8000
```

### 3. Open in Browser

- **Web Portal**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive API Docs (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative API Docs (ReDoc)**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Running Automated Tests

Run the test suite with `pytest`:

```bash
source .venv/bin/activate
pytest -v
```

The test suite runs against an isolated, high-speed in-memory SQLite database verifying:
- Successful account registration and database persistence
- Bcrypt password hash verification
- Duplicate email and username conflict handling (HTTP 409)
- Weak password and malformed email validation errors (HTTP 422)
- Login authentication and JWT generation
- Protected route verification (`/api/auth/me`)

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description | Protected |
|--------|----------|-------------|-----------|
| `POST` | `/api/auth/signup` | Register a new user and receive a JWT token | No |
| `POST` | `/api/auth/login` | Log in with username/email and password | No |
| `GET`  | `/api/auth/me` | Fetch authenticated user's profile | **Yes (Bearer)** |
| `GET`  | `/api/users` | List registered users from SQLite database | No (Demo) |
| `GET`  | `/` | Web application portal (HTML/JS/CSS) | No |
| `GET`  | `/docs` | Swagger interactive API documentation | No |
