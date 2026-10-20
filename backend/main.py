import shutil
import uuid
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import List, Optional

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.auth import (
    create_access_token,
    create_password_reset_token,
    create_verification_token,
    get_current_user,
    hash_password,
    send_password_reset_email,
    send_verification_email,
    verify_email_token,
    verify_password,
    verify_password_reset_token,
)
from backend.database import Base, engine, get_db
from backend.models import User, Availability
from backend.schemas import (
    AvailabilityCreate,
    AvailabilityResponse,
    ForgotPasswordRequest,
    MessageResponse,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads" / "avatars"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="User Authentication API",
    description="FastAPI backend with SQLite database, secure password hashing, and email verification",
    version="1.2.0",
    lifespan=lifespan,
)

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
    existing_user_by_username = db.query(User).filter(User.username == user_in.username).first()
    if existing_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this username already exists.",
        )

    existing_user_by_email = db.query(User).filter(User.email == user_in.email).first()
    if existing_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )

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
    user = db.query(User).filter((User.email == identifier) | (User.username == identifier)).first()
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


@app.post(
    "/api/auth/forgot-password",
    response_model=MessageResponse,
    summary="Request a password reset link via email",
)
def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == request.email.strip().lower()).first()
    if not user or not user.is_active:
        return MessageResponse(
            message="If an account with this email exists, a password reset link has been sent."
        )

    reset_token = create_password_reset_token(user)
    background_tasks.add_task(send_password_reset_email, user.email, reset_token)
    return MessageResponse(
        message="If an account with this email exists, a password reset link has been sent."
    )


@app.get(
    "/api/auth/verify-reset-token",
    response_model=MessageResponse,
    summary="Verify if a password reset token is valid and unexpired",
)
def verify_reset_token(token: str, db: Session = Depends(get_db)):
    user = verify_password_reset_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is invalid or has expired.",
        )
    return MessageResponse(message="Password reset token is valid.")


@app.post(
    "/api/auth/reset-password",
    response_model=MessageResponse,
    summary="Reset user password using a valid reset token",
)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    user = verify_password_reset_token(request.token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is invalid or has expired.",
        )

    user.hashed_password = hash_password(request.password)
    user.is_verified = True
    db.commit()
    return MessageResponse(
        message="Your password has been successfully reset. You can now log in."
    )


@app.get(
    "/api/auth/me",
    response_model=UserResponse,
    summary="Get profile of currently logged-in user",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post(
    "/api/users/me/avatar",
    response_model=UserResponse,
    summary="Upload user avatar image",
)
def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Allowed formats: JPEG, PNG, WEBP, GIF.",
        )

    ext = Path(file.filename or "").suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        ext = ".png"

    unique_filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = UPLOAD_DIR / unique_filename

    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    current_user.avatar_url = f"/media/avatars/{unique_filename}"
    db.commit()
    db.refresh(current_user)

    return current_user


# --- Availability Endpoints ---
@app.get(
    "/api/availability",
    response_model=List[AvailabilityResponse],
    summary="Get current user availability slots",
)
def get_user_availability(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Availability).filter(Availability.user_id == current_user.id)
    if start_date:
        query = query.filter(Availability.date >= start_date)
    if end_date:
        query = query.filter(Availability.date <= end_date)
    return query.order_by(Availability.date.asc(), Availability.start_time.asc()).all()


@app.post(
    "/api/availability",
    response_model=AvailabilityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an availability slot",
)
def add_availability(
    slot_in: AvailabilityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    slot = Availability(
        user_id=current_user.id,
        date=slot_in.date,
        start_time=slot_in.start_time,
        end_time=slot_in.end_time,
        title=slot_in.title or "Available",
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@app.delete(
    "/api/availability/{slot_id}",
    response_model=MessageResponse,
    summary="Delete an availability slot",
)
def delete_availability(
    slot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    slot = (
        db.query(Availability)
        .filter(Availability.id == slot_id, Availability.user_id == current_user.id)
        .first()
    )
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability slot not found.",
        )
    db.delete(slot)
    db.commit()
    return MessageResponse(message="Availability slot deleted successfully.")


@app.get(
    "/api/users",
    response_model=List[UserResponse],
    summary="List registered users",
)
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id.desc()).all()


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

app.mount("/media/avatars", StaticFiles(directory=str(UPLOAD_DIR)), name="avatars")


@app.get("/", include_in_schema=False)
@app.get("/reset-password", include_in_schema=False)
def index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "User Auth API is running. Access /docs for interactive Swagger documentation."
    }