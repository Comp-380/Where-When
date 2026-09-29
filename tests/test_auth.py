import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.auth import verify_password
from backend.database import Base, get_db
from backend.main import app
from backend.models import User

# Use an in-memory SQLite database for fast, isolated tests
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_signup_successful():
    response = client.post(
        "/api/auth/signup",
        json={
            "username": "alice_wonder",
            "email": "alice@example.com",
            "full_name": "Alice Wonderland",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "alice_wonder"
    assert data["user"]["email"] == "alice@example.com"
    assert data["user"]["full_name"] == "Alice Wonderland"
    assert "password" not in data["user"]

    # Verify directly in DB that password is encrypted
    db = TestingSessionLocal()
    user_in_db = db.query(User).filter(User.username == "alice_wonder").first()
    assert user_in_db is not None
    assert user_in_db.hashed_password != "Password123!"
    assert verify_password("Password123!", user_in_db.hashed_password)
    db.close()


def test_signup_duplicate_username():
    payload = {
        "username": "duplicate_user",
        "email": "first@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    r1 = client.post("/api/auth/signup", json=payload)
    assert r1.status_code == 201

    payload2 = {
        "username": "duplicate_user",
        "email": "second@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    r2 = client.post("/api/auth/signup", json=payload2)
    assert r2.status_code == 409
    assert "username already exists" in r2.json()["detail"].lower()


def test_signup_duplicate_email():
    payload = {
        "username": "first_user",
        "email": "shared@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    r1 = client.post("/api/auth/signup", json=payload)
    assert r1.status_code == 201

    payload2 = {
        "username": "second_user",
        "email": "shared@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    r2 = client.post("/api/auth/signup", json=payload2)
    assert r2.status_code == 409
    assert "email address already exists" in r2.json()["detail"].lower()


def test_signup_validation_errors():
    # Invalid email
    r_bad_email = client.post(
        "/api/auth/signup",
        json={
            "username": "testuser",
            "email": "not-an-email",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }
    )
    assert r_bad_email.status_code == 422

    # Weak password (no number or special character)
    r_weak_pwd = client.post(
        "/api/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "weakpassword",
            "confirm_password": "weakpassword"
        }
    )
    assert r_weak_pwd.status_code == 422

    # Mismatched passwords
    r_mismatch = client.post(
        "/api/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
            "confirm_password": "Password456!"
        }
    )
    assert r_mismatch.status_code == 422


def test_login_flow():
    # Register user first
    client.post(
        "/api/auth/signup",
        json={
            "username": "bob_builder",
            "email": "bob@example.com",
            "password": "SecurePassword1!",
            "confirm_password": "SecurePassword1!"
        }
    )

    # Login with username
    r_login_user = client.post(
        "/api/auth/login",
        json={"identifier": "bob_builder", "password": "SecurePassword1!"}
    )
    assert r_login_user.status_code == 200
    token = r_login_user.json()["access_token"]
    assert token

    # Login with email
    r_login_email = client.post(
        "/api/auth/login",
        json={"identifier": "bob@example.com", "password": "SecurePassword1!"}
    )
    assert r_login_email.status_code == 200

    # Login with wrong password
    r_wrong_pwd = client.post(
        "/api/auth/login",
        json={"identifier": "bob_builder", "password": "WrongPassword!"}
    )
    assert r_wrong_pwd.status_code == 401

    # Protected route with token
    r_me = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r_me.status_code == 200
    assert r_me.json()["username"] == "bob_builder"

    # Protected route without token
    r_me_unauth = client.get("/api/auth/me")
    assert r_me_unauth.status_code == 401


def test_list_users_endpoint():
    # Register two users
    client.post(
        "/api/auth/signup",
        json={
            "username": "user_one",
            "email": "user1@example.com",
            "password": "Password1!",
            "confirm_password": "Password1!"
        }
    )
    client.post(
        "/api/auth/signup",
        json={
            "username": "user_two",
            "email": "user2@example.com",
            "password": "Password2@",
            "confirm_password": "Password2@"
        }
    )

    r_users = client.get("/api/users")
    assert r_users.status_code == 200
    users = r_users.json()
    assert len(users) >= 2
    usernames = [u["username"] for u in users]
    assert "user_one" in usernames
    assert "user_two" in usernames


def test_root_serves_html():
    r = client.get("/")
    assert r.status_code == 200
    assert "SecureAuth" in r.text
