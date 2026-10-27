from datetime import date, time
import pytest
from backend.availability_service import (
    time_to_minutes,
    minutes_to_time,
    merge_intervals,
    compute_mutual_intervals,
)
from backend.auth import create_access_token, hash_password
from backend.models import User, Availability, Group, GroupMember
from tests.testing_db import client, TestingSessionLocal



def test_time_conversions():
    t = time(10, 30)
    mins = time_to_minutes(t)
    assert mins == 630
    assert minutes_to_time(mins) == t


def test_user_a_10_to_2_and_user_b_11_to_1():
    """
    Core requirement test:
    If someone is free from 10-2 (10:00 - 14:00)
    and someone else is free from 11-1 (11:00 - 13:00)
    11-1 (11:00 - 13:00) must be shown as a shared free time.
    """
    user_intervals = {
        "alice": [(time_to_minutes(time(10, 0)), time_to_minutes(time(14, 0)))],  # 10:00 - 14:00
        "bob": [(time_to_minutes(time(11, 0)), time_to_minutes(time(13, 0)))],    # 11:00 - 13:00
    }
    result = compute_mutual_intervals(user_intervals, total_group_members=2)
    shared = result["shared_slots"]

    assert len(shared) == 1
    slot = shared[0]
    assert slot["start"] == time_to_minutes(time(11, 0))  # 11:00
    assert slot["end"] == time_to_minutes(time(13, 0))    # 13:00
    assert slot["count"] == 2
    assert slot["users"] == ["alice", "bob"]
    assert minutes_to_time(slot["start"]) == time(11, 0)
    assert minutes_to_time(slot["end"]) == time(13, 0)


def test_disjoint_intervals():
    user_intervals = {
        "alice": [(time_to_minutes(time(9, 0)), time_to_minutes(time(11, 0)))],
        "bob": [(time_to_minutes(time(13, 0)), time_to_minutes(time(15, 0)))],
    }
    result = compute_mutual_intervals(user_intervals, total_group_members=2)
    assert len(result["shared_slots"]) == 0
    assert len(result["partial_slots"]) == 0


def test_touching_intervals_do_not_overlap():
    user_intervals = {
        "alice": [(time_to_minutes(time(9, 0)), time_to_minutes(time(11, 0)))],
        "bob": [(time_to_minutes(time(11, 0)), time_to_minutes(time(13, 0)))],
    }
    result = compute_mutual_intervals(user_intervals, total_group_members=2)
    assert len(result["shared_slots"]) == 0


def test_multiple_shared_intervals_on_same_day():
    user_intervals = {
        "alice": [
            (time_to_minutes(time(9, 0)), time_to_minutes(time(12, 0))),
            (time_to_minutes(time(14, 0)), time_to_minutes(time(17, 0))),
        ],
        "bob": [
            (time_to_minutes(time(10, 0)), time_to_minutes(time(11, 0))),
            (time_to_minutes(time(15, 0)), time_to_minutes(time(18, 0))),
        ],
    }
    result = compute_mutual_intervals(user_intervals, total_group_members=2)
    shared = result["shared_slots"]
    assert len(shared) == 2
    assert shared[0]["start"] == time_to_minutes(time(10, 0))
    assert shared[0]["end"] == time_to_minutes(time(11, 0))
    assert shared[1]["start"] == time_to_minutes(time(15, 0))
    assert shared[1]["end"] == time_to_minutes(time(17, 0))


def test_three_members_partial_vs_full():
    user_intervals = {
        "alice": [(time_to_minutes(time(10, 0)), time_to_minutes(time(14, 0)))],
        "bob": [(time_to_minutes(time(11, 0)), time_to_minutes(time(13, 0)))],
        "charlie": [(time_to_minutes(time(12, 0)), time_to_minutes(time(15, 0)))],
    }
    result = compute_mutual_intervals(user_intervals, total_group_members=3)
    shared = result["shared_slots"]
    assert len(shared) == 1
    assert shared[0]["start"] == time_to_minutes(time(12, 0))
    assert shared[0]["end"] == time_to_minutes(time(13, 0))
    assert shared[0]["count"] == 3
    assert shared[0]["users"] == ["alice", "bob", "charlie"]

    partial = result["partial_slots"]
    assert any(p["start"] == time_to_minutes(time(11, 0)) and p["end"] == time_to_minutes(time(12, 0)) for p in partial)


def test_group_availability_endpoint_10_to_2_and_11_to_1():
    """
    End-to-end integration test:
    Create a group with Alice and Bob.
    Alice is free 10:00 - 14:00 (10-2).
    Bob is free 11:00 - 13:00 (11-1).
    Verify GET /api/groups/{group_id}/availability returns:
      - Individual schedules: Alice (10-2), Bob (11-1)
      - Shared slots: 11:00 - 13:00 (11-1 is shown)
    """
    db = TestingSessionLocal()
    alice = User(
        username="alice",
        email="alice@example.com",
        full_name="Alice Wonderland",
        hashed_password=hash_password("Password123!"),
        is_active=True,
        is_verified=True,
    )
    bob = User(
        username="bob",
        email="bob@example.com",
        full_name="Bob Builder",
        hashed_password=hash_password("Password123!"),
        is_active=True,
        is_verified=True,
    )
    db.add_all([alice, bob])
    db.commit()
    db.refresh(alice)
    db.refresh(bob)

    # Create Group
    group = Group(name="Weekend Hangout", owner_id=alice.id)
    db.add(group)
    db.commit()
    db.refresh(group)

    # Add Members
    db.add_all([
        GroupMember(group_id=group.id, user_id=alice.id, role="owner"),
        GroupMember(group_id=group.id, user_id=bob.id, role="member"),
    ])
    db.commit()

    # Add Alice Availability: 10:00 - 14:00 on 2026-10-25
    slot_alice = Availability(
        user_id=alice.id,
        date=date(2026, 10, 25),
        start_time=time(10, 0),
        end_time=time(14, 0),
        title="Alice Free Hours",
    )
    # Add Bob Availability: 11:00 - 13:00 on 2026-10-25
    slot_bob = Availability(
        user_id=bob.id,
        date=date(2026, 10, 25),
        start_time=time(11, 0),
        end_time=time(13, 0),
        title="Bob Free Hours",
    )
    db.add_all([slot_alice, slot_bob])
    db.commit()

    alice_id = alice.id
    group_id = group.id
    db.close()

    # Authenticate as Alice
    token = create_access_token(data={"sub": str(alice_id)})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(f"/api/groups/{group_id}/availability", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["group_id"] == group.id
    assert data["group_name"] == "Weekend Hangout"
    assert data["total_members"] == 2

    # Check individual member schedules
    members = {m["username"]: m for m in data["members"]}
    assert "alice" in members
    assert "bob" in members
    assert len(members["alice"]["availabilities"]) == 1
    assert members["alice"]["availabilities"][0]["start_time"] == "10:00:00"
    assert members["alice"]["availabilities"][0]["end_time"] == "14:00:00"

    assert len(members["bob"]["availabilities"]) == 1
    assert members["bob"]["availabilities"][0]["start_time"] == "11:00:00"
    assert members["bob"]["availabilities"][0]["end_time"] == "13:00:00"

    # Check shared slots: 11-1 is shown!
    shared = data["shared_slots"]
    assert len(shared) == 1
    assert shared[0]["date"] == "2026-10-25"
    assert shared[0]["start_time"] == "11:00:00"
    assert shared[0]["end_time"] == "13:00:00"
    assert shared[0]["available_member_count"] == 2
    assert shared[0]["total_member_count"] == 2
    assert shared[0]["is_everyone"] is True
    assert set(shared[0]["available_users"]) == {"alice", "bob"}


def test_group_availability_filters_and_permissions():
    db = TestingSessionLocal()
    alice = User(
        username="alice_perm",
        email="alice_perm@example.com",
        full_name="Alice P",
        hashed_password=hash_password("Password123!"),
        is_active=True,
        is_verified=True,
    )
    bob = User(
        username="bob_perm",
        email="bob_perm@example.com",
        full_name="Bob P",
        hashed_password=hash_password("Password123!"),
        is_active=True,
        is_verified=True,
    )
    charlie = User(
        username="charlie_stranger",
        email="charlie@example.com",
        full_name="Charlie Stranger",
        hashed_password=hash_password("Password123!"),
        is_active=True,
        is_verified=True,
    )
    db.add_all([alice, bob, charlie])
    db.commit()

    group = Group(name="Project Circle", owner_id=alice.id)
    db.add(group)
    db.commit()

    db.add_all([
        GroupMember(group_id=group.id, user_id=alice.id, role="owner"),
        GroupMember(group_id=group.id, user_id=bob.id, role="member"),
    ])
    db.commit()

    # Slot on 2026-10-25
    s1 = Availability(user_id=alice.id, date=date(2026, 10, 25), start_time=time(10, 0), end_time=time(12, 0))
    s2 = Availability(user_id=bob.id, date=date(2026, 10, 25), start_time=time(10, 0), end_time=time(12, 0))
    # Slot on 2026-11-01
    s3 = Availability(user_id=alice.id, date=date(2026, 11, 1), start_time=time(14, 0), end_time=time(16, 0))
    s4 = Availability(user_id=bob.id, date=date(2026, 11, 1), start_time=time(14, 0), end_time=time(16, 0))
    db.add_all([s1, s2, s3, s4])
    db.commit()

    alice_id = alice.id
    charlie_id = charlie.id
    group_id = group.id
    db.close()

    alice_token = create_access_token(data={"sub": str(alice_id)})
    charlie_token = create_access_token(data={"sub": str(charlie_id)})

    # Charlie is not a member -> 403 Forbidden
    res = client.get(f"/api/groups/{group_id}/availability", headers={"Authorization": f"Bearer {charlie_token}"})
    assert res.status_code == 403

    # Non-existent group -> 404
    res = client.get("/api/groups/99999/availability", headers={"Authorization": f"Bearer {alice_token}"})
    assert res.status_code == 404

    # Alice queries with date filter (only Oct 2026)
    res = client.get(
        f"/api/groups/{group_id}/availability?start_date=2026-10-01&end_date=2026-10-31",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["shared_slots"]) == 1
    assert data["shared_slots"][0]["date"] == "2026-10-25"
