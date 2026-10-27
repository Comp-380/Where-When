import pytest
from backend.auth import verify_password
from backend.models import User
from tests.testing_db import client, TestingSessionLocal


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
    assert "verify" in data["message"].lower()

    # Verify directly in DB that user was created, is unverified, and password is encrypted
    db = TestingSessionLocal()
    user_in_db = db.query(User).filter(User.username == "alice_wonder").first()
    assert user_in_db is not None
    assert user_in_db.email == "alice@example.com"
    assert user_in_db.full_name == "Alice Wonderland"
    assert user_in_db.is_verified is False
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

    # Login before verification returns 403 Forbidden
    r_unverified = client.post(
        "/api/auth/login",
        json={"identifier": "bob_builder", "password": "SecurePassword1!"}
    )
    assert r_unverified.status_code == 403
    assert "verify" in r_unverified.json()["detail"].lower()

    # Manually verify the user in database
    db = TestingSessionLocal()
    bob = db.query(User).filter(User.username == "bob_builder").first()
    bob.is_verified = True
    db.commit()
    db.close()

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


def test_email_verification_flow():
    from backend.auth import create_verification_token

    # Register user
    r_signup = client.post(
        "/api/auth/signup",
        json={
            "username": "charlie_brown",
            "email": "charlie@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }
    )
    assert r_signup.status_code == 201

    # Unverified login fails
    r_login = client.post(
        "/api/auth/login",
        json={"identifier": "charlie_brown", "password": "Password123!"}
    )
    assert r_login.status_code == 403

    # Verification with invalid token fails
    r_bad = client.get("/api/auth/verify?token=invalid.token")
    assert r_bad.status_code == 400

    # Verification with valid token succeeds
    token = create_verification_token("charlie@example.com")
    r_verify = client.get(f"/api/auth/verify?token={token}")
    assert r_verify.status_code == 200
    assert "successfully verified" in r_verify.json()["message"].lower()

    # Repeated verification notes already verified
    r_again = client.get(f"/api/auth/verify?token={token}")
    assert r_again.status_code == 200
    assert "already verified" in r_again.json()["message"].lower()

    # Login now succeeds
    r_login_ok = client.post(
        "/api/auth/login",
        json={"identifier": "charlie_brown", "password": "Password123!"}
    )
    assert r_login_ok.status_code == 200


def test_resend_verification():
    # Non-existent user returns generic 200
    r_none = client.post(
        "/api/auth/resend-verification",
        json={"email": "nobody@example.com"}
    )
    assert r_none.status_code == 200

    # Existing user
    client.post(
        "/api/auth/signup",
        json={
            "username": "dan_dare",
            "email": "dan@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }
    )
    r_resend = client.post(
        "/api/auth/resend-verification",
        json={"email": "dan@example.com"}
    )
    assert r_resend.status_code == 200


def test_password_reset_flow():
    from backend.auth import create_password_reset_token

    # 1. Register user and verify
    client.post(
        "/api/auth/signup",
        json={
            "username": "eve_hacker",
            "email": "eve@example.com",
            "password": "OldPassword1!",
            "confirm_password": "OldPassword1!"
        }
    )
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "eve@example.com").first()
    user.is_verified = True
    db.commit()

    # 2. Forgot password request for non-existent email returns generic message
    r_nonexistent = client.post(
        "/api/auth/forgot-password",
        json={"email": "unknown@example.com"}
    )
    assert r_nonexistent.status_code == 200
    assert "reset link has been sent" in r_nonexistent.json()["message"]

    # 3. Forgot password request for real email returns generic message
    r_forgot = client.post(
        "/api/auth/forgot-password",
        json={"email": "eve@example.com"}
    )
    assert r_forgot.status_code == 200
    assert "reset link has been sent" in r_forgot.json()["message"]

    # 4. Generate reset token
    reset_token = create_password_reset_token(user)
    db.close()

    # 5. Verify reset token endpoint
    r_verify_bad = client.get("/api/auth/verify-reset-token?token=bad.token")
    assert r_verify_bad.status_code == 400

    r_verify_good = client.get(f"/api/auth/verify-reset-token?token={reset_token}")
    assert r_verify_good.status_code == 200

    # 6. Weak password validation
    r_weak = client.post(
        "/api/auth/reset-password",
        json={
            "token": reset_token,
            "password": "weak",
            "confirm_password": "weak"
        }
    )
    assert r_weak.status_code == 422

    # 7. Mismatched passwords validation
    r_mismatch = client.post(
        "/api/auth/reset-password",
        json={
            "token": reset_token,
            "password": "NewSecurePassword1!",
            "confirm_password": "DifferentPassword1!"
        }
    )
    assert r_mismatch.status_code == 422

    # 8. Reset with bad token
    r_bad_tok = client.post(
        "/api/auth/reset-password",
        json={
            "token": "invalid.token",
            "password": "NewSecurePassword1!",
            "confirm_password": "NewSecurePassword1!"
        }
    )
    assert r_bad_tok.status_code == 400

    # 9. Successful password reset
    r_reset = client.post(
        "/api/auth/reset-password",
        json={
            "token": reset_token,
            "password": "NewSecurePassword1!",
            "confirm_password": "NewSecurePassword1!"
        }
    )
    assert r_reset.status_code == 200
    assert "successfully reset" in r_reset.json()["message"].lower()

    # 10. Old password fails
    r_old_login = client.post(
        "/api/auth/login",
        json={"identifier": "eve@example.com", "password": "OldPassword1!"}
    )
    assert r_old_login.status_code == 401

    # 11. New password succeeds
    r_new_login = client.post(
        "/api/auth/login",
        json={"identifier": "eve@example.com", "password": "NewSecurePassword1!"}
    )
    assert r_new_login.status_code == 200
    assert "access_token" in r_new_login.json()

    # 12. Single-use token: repeating reset with the same token fails
    r_reuse = client.post(
        "/api/auth/reset-password",
        json={
            "token": reset_token,
            "password": "YetAnotherPassword1!",
            "confirm_password": "YetAnotherPassword1!"
        }
    )
    assert r_reuse.status_code == 400


def test_reset_password_verifies_unverified_account():
    from backend.auth import create_password_reset_token

    # User signs up but is unverified
    client.post(
        "/api/auth/signup",
        json={
            "username": "frank_fresh",
            "email": "frank@example.com",
            "password": "InitialPassword1!",
            "confirm_password": "InitialPassword1!"
        }
    )
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "frank@example.com").first()
    assert user.is_verified is False
    token = create_password_reset_token(user)
    db.close()

    # Reset password via email token
    r_reset = client.post(
        "/api/auth/reset-password",
        json={
            "token": token,
            "password": "BrandNewPassword1!",
            "confirm_password": "BrandNewPassword1!"
        }
    )
    assert r_reset.status_code == 200

    # User is now verified and can log in with new password
    r_login = client.post(
        "/api/auth/login",
        json={"identifier": "frank_fresh", "password": "BrandNewPassword1!"}
    )
    assert r_login.status_code == 200


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
