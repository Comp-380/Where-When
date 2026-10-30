import secrets
import shutil
import uuid
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
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
from backend.availability_service import (
    compute_mutual_intervals,
    minutes_to_time,
    time_to_minutes,
)
from backend.database import Base, engine, get_db, initialize_database
from backend.models import User, Availability, Group, GroupMember, generate_invite_code
from backend.schemas import (
    AvailabilityCreate,
    AvailabilityResponse,
    CommonAvailabilitySlot,
    ForgotPasswordRequest,
    GroupAvailabilityResponse,
    GroupCreate,
    GroupJoinRequest,
    GroupMemberResponse,
    GroupResponse,
    MemberAddRequest,
    MessageResponse,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads" / "avatars"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database(engine)
    yield


app = FastAPI(
    title="User Authentication API",
    description="FastAPI backend with SQLite database, secure password hashing, and email verification",
    version="1.3.0",
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


def generate_unique_group_code(db: Session) -> str:
    """Generate a unique invite code for a new group."""
    for _ in range(10):
        code = generate_invite_code()
        if not db.query(Group).filter(Group.invite_code == code).first():
            return code
    return generate_invite_code() + secrets.token_hex(2).upper()


# --- Group Endpoints ---
@app.post(
    "/api/groups",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new group record",
)
def create_group(
    group_in: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    code = generate_unique_group_code(db)
    new_group = Group(
        name=group_in.name,
        description=group_in.description,
        owner_id=current_user.id,
        invite_code=code,
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    membership = GroupMember(
        group_id=new_group.id,
        user_id=current_user.id,
        role="owner",
    )
    db.add(membership)
    db.commit()

    return GroupResponse(
        id=new_group.id,
        name=new_group.name,
        description=new_group.description,
        owner_id=new_group.owner_id,
        invite_code=new_group.invite_code,
        member_count=1,
        created_at=new_group.created_at,
    )


@app.get(
    "/api/groups",
    response_model=List[GroupResponse],
    summary="List groups the current user belongs to",
)
def get_user_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memberships = (
        db.query(GroupMember)
        .filter(GroupMember.user_id == current_user.id)
        .all()
    )
    group_ids = [m.group_id for m in memberships]
    groups = db.query(Group).filter(Group.id.in_(group_ids)).order_by(Group.id.desc()).all()

    response = []
    for g in groups:
        count = db.query(GroupMember).filter(GroupMember.group_id == g.id).count()
        response.append(
            GroupResponse(
                id=g.id,
                name=g.name,
                description=g.description,
                owner_id=g.owner_id,
                invite_code=g.invite_code,
                member_count=count,
                created_at=g.created_at,
                group_photo_url=g.group_photo_url,
            )
        )
    return response


@app.post(
    "/api/groups/join",
    response_model=GroupResponse,
    status_code=status.HTTP_200_OK,
    summary="Join an existing group using an invite code",
)
def join_group(
    req: GroupJoinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    code = req.invite_code.strip().upper()
    group = db.query(Group).filter(func.upper(Group.invite_code) == code).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite code. Group not found.",
        )

    # Check if user is already a member
    existing_mem = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group.id, GroupMember.user_id == current_user.id)
        .first()
    )
    if existing_mem:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already a member of this group.",
        )

    membership = GroupMember(
        group_id=group.id,
        user_id=current_user.id,
        role="member",
    )
    db.add(membership)
    db.commit()

    count = db.query(GroupMember).filter(GroupMember.group_id == group.id).count()

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        owner_id=group.owner_id,
        invite_code=group.invite_code,
        member_count=count,
        created_at=group.created_at,
    )


@app.post(
    "/api/groups/{group_id}/leave",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Leave a group that you are a member of",
)
@app.delete(
    "/api/groups/{group_id}/leave",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Leave a group that you are a member of",
)
def leave_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")

    if group.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group owners cannot leave the group. Delete or transfer the group instead.",
        )

    membership = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id)
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a member of this group.",
        )

    db.delete(membership)
    db.commit()

    return MessageResponse(message=f"You have left '{group.name}'.")


@app.get(
    "/api/groups/{group_id}/availability",
    response_model=GroupAvailabilityResponse,
    summary="Get group members' schedules and shared times when members are free",
)
def get_group_availability(
    group_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user_ids: Optional[List[int]] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")

    user_mem = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id)
        .first()
    )
    if not user_mem:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    all_members = (
        db.query(GroupMember, User)
        .join(User, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id)
        .all()
    )

    filtered_members = all_members
    if user_ids:
        filtered_members = [(m, u) for m, u in all_members if u.id in user_ids]
        if not filtered_members:
            filtered_members = all_members

    members_response = []
    dates_map: Dict[date, Dict[str, List[Tuple[int, int]]]] = {}

    for mem, usr in filtered_members:
        query = db.query(Availability).filter(Availability.user_id == usr.id)
        if start_date:
            query = query.filter(Availability.date >= start_date)
        if end_date:
            query = query.filter(Availability.date <= end_date)
        slots = query.order_by(Availability.date.asc(), Availability.start_time.asc()).all()

        members_response.append(
            GroupMemberResponse(
                id=mem.id,
                user_id=usr.id,
                username=usr.username,
                full_name=usr.full_name,
                role=mem.role,
                joined_at=mem.joined_at,
                availabilities=[AvailabilityResponse.model_validate(s) for s in slots],
            )
        )

        for s in slots:
            if s.date not in dates_map:
                dates_map[s.date] = {}
            if usr.username not in dates_map[s.date]:
                dates_map[s.date][usr.username] = []
            dates_map[s.date][usr.username].append(
                (time_to_minutes(s.start_time), time_to_minutes(s.end_time))
            )

    total_considered = len(filtered_members)
    all_shared_slots: List[CommonAvailabilitySlot] = []
    all_partial_slots: List[CommonAvailabilitySlot] = []

    for d in sorted(dates_map.keys()):
        day_user_intervals = dates_map[d]
        mutual = compute_mutual_intervals(day_user_intervals, total_considered)

        for slot in mutual["shared_slots"]:
            all_shared_slots.append(
                CommonAvailabilitySlot(
                    date=d,
                    start_time=minutes_to_time(slot["start"]),
                    end_time=minutes_to_time(slot["end"]),
                    available_member_count=slot["count"],
                    total_member_count=total_considered,
                    is_everyone=True,
                    available_users=slot["users"],
                )
            )

        for slot in mutual["partial_slots"]:
            is_ev = slot["count"] == total_considered
            all_partial_slots.append(
                CommonAvailabilitySlot(
                    date=d,
                    start_time=minutes_to_time(slot["start"]),
                    end_time=minutes_to_time(slot["end"]),
                    available_member_count=slot["count"],
                    total_member_count=total_considered,
                    is_everyone=is_ev,
                    available_users=slot["users"],
                )
            )

    return GroupAvailabilityResponse(
        group_id=group.id,
        group_name=group.name,
        total_members=total_considered,
        members=members_response,
        shared_slots=all_shared_slots,
        partial_slots=all_partial_slots,
    )



@app.get(
    "/api/groups/{group_id}/members",
    response_model=List[GroupMemberResponse],
    summary="List members of a specific group along with their availability",
)
def get_group_members(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_mem = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id)
        .first()
    )
    if not user_mem:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    members = (
        db.query(GroupMember, User)
        .join(User, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id)
        .all()
    )

    response = []
    for mem, usr in members:
        slots = (
            db.query(Availability)
            .filter(Availability.user_id == usr.id)
            .order_by(Availability.date.asc(), Availability.start_time.asc())
            .all()
        )
        response.append(
            GroupMemberResponse(
                id=mem.id,
                user_id=usr.id,
                username=usr.username,
                full_name=usr.full_name,
                role=mem.role,
                joined_at=mem.joined_at,
                availabilities=[AvailabilityResponse.model_validate(s) for s in slots],
            )
        )

    return response


@app.post(
    "/api/groups/{group_id}/members",
    response_model=MessageResponse,
    summary="Add a user to the group by username or email",
)
def add_group_member(
    group_id: int,
    req: MemberAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")

    if group.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the group owner can add members.")

    identifier = req.identifier.strip().lower()
    target_user = (
        db.query(User)
        .filter((User.username == identifier) | (User.email == identifier))
        .first()
    )
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    existing_mem = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == target_user.id)
        .first()
    )
    if existing_mem:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already in this group.")

    new_mem = GroupMember(group_id=group_id, user_id=target_user.id, role="member")
    db.add(new_mem)
    db.commit()

    return MessageResponse(message=f"Added @{target_user.username} to {group.name} successfully.")


@app.delete(
    "/api/groups/{group_id}/members/{user_id}",
    response_model=MessageResponse,
    summary="Remove a member from the group (owner only)",
)
def remove_group_member(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")

    if group.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can remove members.")

    if user_id == group.owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The owner cannot be removed from the group.")

    membership = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found in this group.")

    db.delete(membership)
    db.commit()

    return MessageResponse(message="Member removed from group successfully.")


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


@app.patch(
    "/api/users/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user_update.username and user_update.username != current_user.username:
        existing = db.query(User).filter(User.username == user_update.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already taken.",
            )
        current_user.username = user_update.username

    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name

    db.commit()
    db.refresh(current_user)
    return current_user


@app.delete(
    "/api/users/me",
    response_model=MessageResponse,
    summary="Delete current user account",
)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.delete(current_user)
    db.commit()
    return MessageResponse(message="Account successfully deleted.")


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

@app.put("/api/groups/{group_id}/photo", response_model=GroupResponse)
async def upload_group_photo(
    group_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Save the file following your app's existing upload structure
    ext = Path(file.filename or "").suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        ext = ".png"
        
    unique_filename = f"group_{group_id}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = UPLOAD_DIR / unique_filename
    
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    group.group_photo_url = f"/media/uploads/{unique_filename}"
    db.commit()
    db.refresh(group)
    return group

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
app.mount("/media/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads_media")

@app.get("/", include_in_schema=False)
@app.get("/reset-password", include_in_schema=False)
def index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "User Auth API is running. Access /docs for interactive Swagger documentation."
    }
