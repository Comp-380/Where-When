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
    - Scoped email verification tokens (24h expiry) and single-use password reset tokens (60m expiry).
    - Single-use invalidation on password reset tokens by fingerprinting active password hash.
    - Anti-enumeration protection on verification and password reset requests.
    - Case-insensitive unique username and email constraints.
  - **Input Validation**: Pydantic schemas validating email format, username restrictions, and password strength policies.

- **Frontend**:
  - **Multi-Mode Views**: Seamless navigation between **Create Account**, **Sign In**, **Forgot Password**, and **Reset Password**.
  - **Live Password Strength Meter**: 5-point evaluation (length, uppercase, lowercase, numbers, special characters) with real-time animated visual bar and checklist.
  - **Email Verification & Password Reset Flows**: Token verification via URL parameters (`?token=...` or `?reset_token=...`), resend verification option, and dedicated password reset form.
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
│   ├── schemas.py       # Pydantic validation models (UserCreate, UserLogin, UserResponse, etc.)
│   └── main.py          # FastAPI application, route handlers & static file serving
├── frontend/
│   ├── index.html       # Web portal markup (Signup, Login, Forgot & Reset Password, Dashboard)
│   ├── css/
│   │   └── style.css    # Responsive styles, dark mode UI, password meter
│   └── js/
│       └── app.js       # Client validation, API requests, session & reset handling
├── tests/
│   ├── __init__.py
│   └── test_auth.py     # Automated test suite (Signup, Login, Email Verification, Password Reset)
├── requirements.txt     # Python package dependencies
├── pytest.ini          # Test runner configuration
├── run.py               # Application entrypoint script
└── README.md
```

---

## 🚀 Quickstart

### 1. Create Virtual Environment

```bash
python3 -m venv .venv
```

### 2. Activate Virtual Environment

- **macOS / Linux (Bash / Zsh)**:
  ```bash
  source .venv/bin/activate
  ```
- **Windows (Command Prompt / PowerShell)**:
  ```powershell
  .venv\Scripts\activate
  ```
- **Fish Shell**:
  ```fish
  source .venv/bin/activate.fish
  ```

*(Or simply run scripts directly without activation using `./.venv/bin/python`)*

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Start the Server

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

### 5. Open in Browser

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
- Email verification flow and unverified login prevention
- Resend verification link behavior
- Password reset request, token validation, password update, and single-use invalidation
- Bcrypt password hash verification
- Duplicate email and username conflict handling (HTTP 409)
- Weak password and malformed email validation errors (HTTP 422)
- Login authentication and JWT generation
- Protected route verification (`/api/auth/me`)

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description | Protected |
|--------|----------|-------------|-----------|
| `POST` | `/api/auth/signup` | Register a new user account (sends email verification) | No |
| `GET`  | `/api/auth/verify` | Verify user email address with token | No |
| `POST` | `/api/auth/resend-verification` | Resend verification email link | No |
| `POST` | `/api/auth/forgot-password` | Request password reset link via email | No |
| `GET`  | `/api/auth/verify-reset-token` | Verify password reset token validity | No |
| `POST` | `/api/auth/reset-password` | Reset password using verified token | No |
| `POST` | `/api/auth/login` | Log in with username/email and password | No |
| `GET`  | `/api/auth/me` | Fetch authenticated user's profile | **Yes (Bearer)** |
| `GET`  | `/api/users` | List registered users from SQLite database | No (Demo) |
| `GET`  | `/` | Web application portal (HTML/JS/CSS) | No |
| `GET`  | `/docs` | Swagger interactive API documentation | No |
