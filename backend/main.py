from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.auth import (
    create_access_token,
    create_verification_token,
    get_current_user,
    hash_password,
    send_verification_email,
    verify_email_token,
    verify_password,
)
from backend.database import Base, engine, get_db
from backend.models import User
from backend.schemas import (
    MessageResponse,
    ResendVerificationRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="User Authentication API",
    description="FastAPI backend with SQLite database, secure password hashing, and email verification",
    version="1.1.0",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/api/auth/signup",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def signup(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # Check if username already exists
    existing_user_by_username = (
        db.query(User).filter(User.username == user_in.username).first()
    )
    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this username already exists.",
        )

    # Check if email already exists
    existing_user_by_email = (
        db.query(User).filter(User.email == user_in.email).first()
    )
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )

    # Hash the password and persist unverified user record
    hashed_pwd = hash_password(user_in.password)
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_pwd,
        is_active=True,
        is_verified=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate token and queue verification email
    verify_token = create_verification_token(new_user.email)
    background_tasks.add_task(send_verification_email, new_user.email, verify_token)

    return MessageResponse(
        message="Registration successful. Please check your email to verify your account before logging in."
    )


@app.get(
    "/api/auth/verify",
    response_model=MessageResponse,
    summary="Verify user email address",
)
def verify_email(token: str, db: Session = Depends(get_db)):
    email = verify_email_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token is invalid or has expired.",
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with this token was not found.",
        )

    if user.is_verified:
        return MessageResponse(message="Email is already verified. You can log in.")

    user.is_verified = True
    db.commit()
    return MessageResponse(message="Email successfully verified. You can now log in.")


@app.post(
    "/api/auth/resend-verification",
    response_model=MessageResponse,
    summary="Resend verification email",
)
def resend_verification(
    request: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == request.email.strip().lower()).first()
    if not user:
        # Generic response to prevent account enumeration
        return MessageResponse(
            message="If an unverified account with this email exists, a verification link has been sent."
        )

    if user.is_verified:
        return MessageResponse(message="This account is already verified.")

    verify_token = create_verification_token(user.email)
    background_tasks.add_task(send_verification_email, user.email, verify_token)
    return MessageResponse(
        message="If an unverified account with this email exists, a verification link has been sent."
    )


@app.post(
    "/api/auth/login",
    response_model=TokenResponse,
    summary="Authenticate and login an existing user",
)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    identifier = login_in.identifier.strip().lower()

    # Query matching email or username
    user = (
        db.query(User)
        .filter((User.email == identifier) | (User.username == identifier))
        .first()
    )

    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please check your username/email and password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user account has been disabled.",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in. Use resend verification if needed.",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@app.get(
    "/api/auth/me",
    response_model=UserResponse,
    summary="Get profile of currently logged-in user",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get(
    "/api/users",
    response_model=List[UserResponse],
    summary="List registered users (for database demo purposes)",
)
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.desc()).all()
    return users


# Mount static assets
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", include_in_schema=False)
def index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "User Auth API is running. Access /docs for interactive Swagger documentation."
    }