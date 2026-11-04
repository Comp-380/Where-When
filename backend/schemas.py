import re
from datetime import date as DateType, time as TimeType, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


def validate_password_complexity(v: str) -> str:
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not re.search(r"[a-z]", v):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not re.search(r"[A-Z]", v):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r"\d", v):
        raise ValueError("Password must contain at least one numeric digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
        raise ValueError("Password must contain at least one special character (e.g. !@#$%^&*).")
    return v


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr = Field(...)
    full_name: Optional[str] = Field(None, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: Optional[str] = Field(None)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain alphanumeric characters, hyphens, and underscores.")
        return v.lower()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return validate_password_complexity(v)

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.confirm_password is not None and self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    street_address: Optional[str] = Field(None, max_length=255)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)


class UserLogin(BaseModel):
    identifier: str = Field(..., description="Email or Username")
    password: str = Field(..., min_length=1, description="Account password")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    street_address: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    message: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(...)
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: Optional[str] = Field(None)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return validate_password_complexity(v)

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.confirm_password is not None and self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


# --- Availability Schemas ---
class AvailabilityCreate(BaseModel):
    date: DateType
    start_time: TimeType
    end_time: TimeType
    title: Optional[str] = "Available"

    @model_validator(mode="after")
    def validate_times(self):
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time.")
        return self


class AvailabilityResponse(BaseModel):
    id: int
    user_id: int
    date: DateType
    start_time: TimeType
    end_time: TimeType
    title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Group Schemas ---
class GroupCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Name of the group")
    description: Optional[str] = Field(None, max_length=255, description="Optional description of the group")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("Group name must be at least 2 characters.")
        return clean


class GroupJoinRequest(BaseModel):
    invite_code: str = Field(..., min_length=4, max_length=64, description="Group invite code")

    @field_validator("invite_code")
    @classmethod
    def validate_invite_code(cls, v: str) -> str:
        clean = v.strip().upper()
        if len(clean) < 4:
            raise ValueError("Invite code must be at least 4 characters.")
        return clean


class MemberAddRequest(BaseModel):
    identifier: str = Field(..., description="Username or email of user to add")


class GroupMemberResponse(BaseModel):
    id: int
    user_id: int
    username: str
    full_name: Optional[str] = None
    role: str
    joined_at: datetime
    availabilities: List[AvailabilityResponse] = []

    model_config = ConfigDict(from_attributes=True)


class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    group_photo_url: Optional[str] = None
    owner_id: int
    invite_code: str
    member_count: int = 1
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GroupPollOptionResponse(BaseModel):
    id: int
    group_id: int
    text: str
    is_default: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PollOptionCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=100)

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Option text cannot be empty.")
        return clean


class PollVoteRequest(BaseModel):
    option_id: int


class PollOptionResponse(BaseModel):
    id: int
    poll_id: int
    text: str
    is_default: bool
    count: int = 0
    percentage: float = 0.0
    voters: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class HangoutPollResponse(BaseModel):
    id: int
    group_id: int
    date: DateType
    start_time: TimeType
    end_time: TimeType
    place: str
    total_votes: int = 0
    my_vote_option_id: Optional[int] = None
    options: List[PollOptionResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommonAvailabilitySlot(BaseModel):
    date: DateType
    start_time: TimeType
    end_time: TimeType
    available_member_count: int
    total_member_count: int
    is_everyone: bool
    available_users: List[str]
    poll: Optional[HangoutPollResponse] = None

    model_config = ConfigDict(from_attributes=True)


class GroupAvailabilityResponse(BaseModel):
    group_id: int
    group_name: str
    total_members: int
    members: List[GroupMemberResponse]
    shared_slots: List[CommonAvailabilitySlot]
    partial_slots: List[CommonAvailabilitySlot] = []
    polls: List[HangoutPollResponse] = []

    model_config = ConfigDict(from_attributes=True)