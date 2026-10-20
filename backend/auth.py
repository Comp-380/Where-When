import logging
import os
import smtplib
import ssl
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User

logger = logging.getLogger("uvicorn.error.auth")

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production-super-safe-key-12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
VERIFY_TOKEN_EXPIRE_HOURS = 24
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "60"))

# SMTP Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@example.com")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with salt rounds."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT token for authentication."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_verification_token(email: str) -> str:
    """Create a scoped short-lived token for email verification."""
    expire = datetime.now(timezone.utc) + timedelta(hours=VERIFY_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": email,
        "type": "email_verification",
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_email_token(token: str) -> Optional[str]:
    """Verify the verification token and extract the user email."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "email_verification":
            return None
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


def send_verification_email(recipient_email: str, token: str):
    """Send verification via SMTP and log the delivery result."""
    verification_link = f"{APP_BASE_URL}/api/auth/verify?token={token}"

    print("\n" + "=" * 60, flush=True)
    print(f"[VERIFICATION LINK FOR {recipient_email}]:", flush=True)
    print(verification_link, flush=True)
    print("=" * 60 + "\n", flush=True)

    if not SMTP_HOST:
        logger.warning("Verification email not sent: SMTP_HOST is not configured.")
        return

    msg = EmailMessage()
    msg["Subject"] = "Verify Your Account"
    msg["From"] = SMTP_FROM
    msg["To"] = recipient_email
    msg.set_content(
        f"Welcome! Please verify your account by clicking the link below:\n\n{verification_link}\n\n"
        f"This link expires in {VERIFY_TOKEN_EXPIRE_HOURS} hours."
    )

    context = ssl.create_default_context()
    try:
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15, context=context) as server:
                if SMTP_USER and SMTP_PASSWORD:
                    server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                if SMTP_USER and SMTP_PASSWORD:
                    server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        logger.info("SMTP server accepted verification email for %s.", recipient_email)
    except Exception as e:
        logger.error(f"Failed to send verification email to {recipient_email}: {e}")


def create_password_reset_token(user: User) -> str:
    """Create a scoped short-lived token for password reset with single-use invalidation."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user.email,
        "type": "password_reset",
        "pwd_sig": user.hashed_password[:16],
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_password_reset_token(token: str, db: Session) -> Optional[User]:
    """Verify the password reset token and return the associated active user if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        email = payload.get("sub")
        pwd_sig = payload.get("pwd_sig")
        if not email or not pwd_sig:
            return None
    except jwt.PyJWTError:
        return None

    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        return None

    if user.hashed_password[:16] != pwd_sig:
        return None

    return user


def send_password_reset_email(recipient_email: str, token: str):
    """Send password reset link via SMTP or print to console."""
    reset_link = f"{APP_BASE_URL}/?reset_token={token}"

    print("\n" + "=" * 60, flush=True)
    print(f"[PASSWORD RESET LINK FOR {recipient_email}]:", flush=True)
    print(reset_link, flush=True)
    print("=" * 60 + "\n", flush=True)

    if not SMTP_HOST:
        return

    msg = EmailMessage()
    msg["Subject"] = "Reset Your Password"
    msg["From"] = SMTP_FROM
    msg["To"] = recipient_email
    msg.set_content(
        f"Hello,\n\nWe received a request to reset your password. You can reset it by clicking the link below:\n\n{reset_link}\n\n"
        f"This link expires in {RESET_TOKEN_EXPIRE_MINUTES} minutes.\n\n"
        f"If you did not request a password reset, please ignore this email and your password will remain unchanged."
    )

    context = ssl.create_default_context()
    try:
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15, context=context) as server:
                if SMTP_USER and SMTP_PASSWORD:
                    server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                if SMTP_USER and SMTP_PASSWORD:
                    server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
    except Exception as e:
        logger.error(f"Failed to send password reset email to {recipient_email}: {e}")


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to retrieve the authenticated user from the Bearer token."""
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise unauthorized_exception

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise unauthorized_exception
        user_id = payload.get("sub")
        if user_id is None:
            raise unauthorized_exception
    except jwt.PyJWTError:
        raise unauthorized_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise unauthorized_exception
    return user