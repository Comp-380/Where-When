import pytest
from backend.auth import hash_password
from backend.models import User
from tests.testing_db import client, TestingSessionLocal


def create_user_and_token(username: str, email: str) -> tuple[int, str]:
    db = TestingSessionLocal()
    user = User(
        username=username,
        email=email,
        full_name=username.capitalize(),
        hashed_password=hash_password("Password123!"),
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id
    db.close()

    res = client.post(
        "/api/auth/login",
        json={"identifier": username, "password": "Password123!"}
    )
    token = res.json()["access_token"]
    return user_id, token


def test_create_group_returns_invite_code():
    _, token = create_user_and_token("alice_c", "alice_c@example.com")
    res = client.post(
        "/api/groups",
        json={"name": "Alice's Squad", "description": "Fun activities"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["name"] == "Alice's Squad"
    assert data["description"] == "Fun activities"
    assert data["member_count"] == 1
    assert "invite_code" in data
    assert len(data["invite_code"]) == 8
    assert data["invite_code"].isupper()


def test_list_groups_includes_invite_code():
    _, token = create_user_and_token("alice_l", "alice_l@example.com")
    client.post(
        "/api/groups",
        json={"name": "Book Club"},
        headers={"Authorization": f"Bearer {token}"},
    )
    res = client.get(
        "/api/groups",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    groups = res.json()
    assert len(groups) == 1
    assert groups[0]["name"] == "Book Club"
    assert "invite_code" in groups[0]
    assert len(groups[0]["invite_code"]) == 8


def test_join_group_flow():
    _, alice_token = create_user_and_token("alice_j", "alice_j@example.com")
    _, bob_token = create_user_and_token("bob_j", "bob_j@example.com")

    # Alice creates a group
    create_res = client.post(
        "/api/groups",
        json={"name": "Hiking Club", "description": "Weekend hikes"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    group_data = create_res.json()
    invite_code = group_data["invite_code"]
    group_id = group_data["id"]

    # Bob joins the group
    join_res = client.post(
        "/api/groups/join",
        json={"invite_code": invite_code},
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert join_res.status_code == 200, join_res.text
    joined_data = join_res.json()
    assert joined_data["id"] == group_id
    assert joined_data["name"] == "Hiking Club"
    assert joined_data["member_count"] == 2

    # Group now appears in Bob's group list
    bob_groups = client.get(
        "/api/groups",
        headers={"Authorization": f"Bearer {bob_token}"},
    ).json()
    assert len(bob_groups) == 1
    assert bob_groups[0]["id"] == group_id
    assert bob_groups[0]["member_count"] == 2

    # Group members endpoint shows both Alice and Bob
    members_res = client.get(
        f"/api/groups/{group_id}/members",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert members_res.status_code == 200
    usernames = [m["username"] for m in members_res.json()]
    assert "alice_j" in usernames
    assert "bob_j" in usernames


def test_join_group_case_insensitive_and_whitespace():
    _, alice_token = create_user_and_token("alice_ci", "alice_ci@example.com")
    _, bob_token = create_user_and_token("bob_ci", "bob_ci@example.com")

    create_res = client.post(
        "/api/groups",
        json={"name": "Cycling Group"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    invite_code = create_res.json()["invite_code"]

    # Bob joins using lowercased and padded invite code
    join_res = client.post(
        "/api/groups/join",
        json={"invite_code": f"  {invite_code.lower()}  "},
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert join_res.status_code == 200
    assert join_res.json()["name"] == "Cycling Group"


def test_join_group_invalid_code():
    _, bob_token = create_user_and_token("bob_inv", "bob_inv@example.com")
    res = client.post(
        "/api/groups/join",
        json={"invite_code": "NONEXIST1"},
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert res.status_code == 404
    assert "Invalid invite code" in res.json()["detail"]


def test_join_group_already_member():
    _, alice_token = create_user_and_token("alice_am", "alice_am@example.com")
    create_res = client.post(
        "/api/groups",
        json={"name": "Alice's Solo Club"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    invite_code = create_res.json()["invite_code"]

    # Alice tries to join her own group
    res = client.post(
        "/api/groups/join",
        json={"invite_code": invite_code},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert res.status_code == 409
    assert "already a member" in res.json()["detail"]


def test_leave_group_member_flow():
    _, alice_token = create_user_and_token("alice_lv", "alice_lv@example.com")
    _, bob_token = create_user_and_token("bob_lv", "bob_lv@example.com")

    create_res = client.post(
        "/api/groups",
        json={"name": "Running Club"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    group_id = create_res.json()["id"]
    invite_code = create_res.json()["invite_code"]

    # Bob joins
    client.post(
        "/api/groups/join",
        json={"invite_code": invite_code},
        headers={"Authorization": f"Bearer {bob_token}"},
    )

    # Bob leaves via POST /api/groups/{id}/leave
    leave_res = client.post(
        f"/api/groups/{group_id}/leave",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert leave_res.status_code == 200
    assert "left" in leave_res.json()["message"].lower()

    # Bob no longer has the group
    bob_groups = client.get(
        "/api/groups",
        headers={"Authorization": f"Bearer {bob_token}"},
    ).json()
    assert len(bob_groups) == 0

    # Alice sees member_count == 1
    alice_groups = client.get(
        "/api/groups",
        headers={"Authorization": f"Bearer {alice_token}"},
    ).json()
    assert alice_groups[0]["member_count"] == 1


def test_leave_group_delete_endpoint():
    _, alice_token = create_user_and_token("alice_del", "alice_del@example.com")
    _, bob_token = create_user_and_token("bob_del", "bob_del@example.com")

    create_res = client.post(
        "/api/groups",
        json={"name": "Chess Club"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    group_id = create_res.json()["id"]
    invite_code = create_res.json()["invite_code"]

    # Bob joins
    client.post(
        "/api/groups/join",
        json={"invite_code": invite_code},
        headers={"Authorization": f"Bearer {bob_token}"},
    )

    # Bob leaves via DELETE /api/groups/{id}/leave
    leave_res = client.delete(
        f"/api/groups/{group_id}/leave",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert leave_res.status_code == 200
    assert "left" in leave_res.json()["message"].lower()


def test_leave_group_owner_cannot_leave():
    _, alice_token = create_user_and_token("alice_own", "alice_own@example.com")
    create_res = client.post(
        "/api/groups",
        json={"name": "Owner Only Club"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    group_id = create_res.json()["id"]

    res = client.post(
        f"/api/groups/{group_id}/leave",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert res.status_code == 400
    assert "owners cannot leave" in res.json()["detail"].lower()


def test_leave_group_not_a_member():
    _, alice_token = create_user_and_token("alice_not", "alice_not@example.com")
    _, bob_token = create_user_and_token("bob_not", "bob_not@example.com")

    create_res = client.post(
        "/api/groups",
        json={"name": "Secret Club"},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    group_id = create_res.json()["id"]

    # Bob tries to leave without having joined
    res = client.post(
        f"/api/groups/{group_id}/leave",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert res.status_code == 404
    assert "not a member" in res.json()["detail"].lower()


def test_join_and_leave_unauthorized():
    res_join = client.post("/api/groups/join", json={"invite_code": "ABC12345"})
    assert res_join.status_code == 401

    res_leave = client.post("/api/groups/1/leave")
    assert res_leave.status_code == 401
