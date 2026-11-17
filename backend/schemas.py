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
    username: Optional[str] = None
    full_name: Optional[str] = None
    street_address: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    max_travel_distance: Optional[int] = None


class UserLogin(BaseModel):
    identifier: str = Field(..., description="Email or Username")
    password: str = Field(..., min_length=1, description="Account password")


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    street_address: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    max_travel_distance: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
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


class PlaceVoteRequest(BaseModel):
    place_name: str

    @field_validator("place_name")
    @classmethod
    def validate_place_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Place name cannot be empty.")
        return clean


class PlaceVoteSummary(BaseModel):
    place_name: str
    count: int = 0
    voters: List[str] = []
    has_voted: bool = False

    model_config = ConfigDict(from_attributes=True)


class HangoutPollResponse(BaseModel):
    id: int
    group_id: int
    date: DateType
    start_time: TimeType
    end_time: TimeType
    place: str
    current_place: Optional[str] = "Not Yet Decided"
    total_votes: int = 0
    my_vote_option_id: Optional[int] = None
    options: List[PollOptionResponse] = []
    place_votes: List[PlaceVoteSummary] = []
    my_place_votes: List[str] = []
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


# --- Place & Entertainment Recommendations Schemas ---
class UserDistanceInfo(BaseModel):
    user_id: int
    username: str
    full_name: Optional[str] = None
    distance_miles: float
    max_distance_miles: Optional[int] = None
    is_within_limit: bool

class ActivityReview(BaseModel):
    """SCRUM-52: Schema for individual activity/venue customer reviews."""
    author_name: str
    rating: float = 5.0
    relative_time: str = "Recently"
    text: str = ""
    author_photo_url: Optional[str] = None

class RecommendationItem(BaseModel):
    id: str
    title: str
    item_type: str = "venue"  # "venue" or "event"
    category: str = "Food & Dining"  # "Food & Dining" or "Entertainment"
    subcategory: str = "Venue"
    address: str = ""
    rating: Optional[float] = None
    user_rating_count: int = 0  # SCRUM-52: Total number of reviews
    price_level: Optional[str] = None
    price_display: Optional[str] = None
    price_tier: Optional[int] = None
    # SCRUM-51: Detailed Activity Information fields
    description: Optional[str] = None
    phone_number: Optional[str] = None
    website_url: Optional[str] = None
    weekday_hours: List[str] = []
    maps_url: Optional[str] = None
    ticket_url: Optional[str] = None
    event_time: Optional[str] = None
    is_open_confirmed: bool = True
    open_hours_text: Optional[str] = None
    # Activity distance metrics
    avg_distance_miles: float
    min_member_distance_miles: Optional[float] = None
    max_member_distance_miles: Optional[float] = None
    distance_from_midpoint: Optional[float] = None
    all_within_limit: bool = True
    user_distances: List[UserDistanceInfo] = []
    # Activity recommendation tags
    match_reasons: List[str] = []
    # SCRUM-52: List of customer reviews
    reviews: List[ActivityReview] = []
    is_mock: bool = False
    source: str = "Live"


class PollRecommendationsResponse(BaseModel):
    poll_id: int
    group_id: int
    category: str
    budget: Optional[str] = None
    max_distance: Optional[float] = None
    within_limits_only: bool = False
    sort_by: Optional[str] = "recommended"
    total_found: int = 0
    midpoint_address: Optional[str] = None
    missing_address_users: List[str] = []
    is_mock_data: bool = False
    data_source_notice: Optional[str] = None
    items: List[RecommendationItem] = []