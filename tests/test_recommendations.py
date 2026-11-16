from datetime import date, time
import pytest
from backend.auth import create_access_token, hash_password
from backend.models import User, Availability, Group, GroupMember, HangoutPoll, PollOption
from backend.recommendation_service import (
    haversine_miles,
    is_venue_open_during_slot,
    get_recommendations_for_poll,
)
from tests.testing_db import client, TestingSessionLocal


def create_user(db, username, email, street="18111 Nordhoff St", state="CA", zip_code="91330", max_dist=25):
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password("Password123!"),
        street_address=street,
        state=state,
        zip_code=zip_code,
        max_travel_distance=max_dist,
        is_verified=True,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_haversine_calculation():
    # Distance between Burbank (34.1808, -118.3090) and Northridge (34.2381, -118.5282) ~ 13 miles
    d = haversine_miles(34.1808, -118.3090, 34.2381, -118.5282)
    assert 11.0 <= d <= 15.0


def test_is_venue_open_during_slot():
    # Friday Nov 13, 2026 (weekday = 4 in Python -> Google day = (4+1)%7 = 5)
    slot_date = date(2026, 11, 13)
    start_time = time(18, 0)  # 6:00 PM
    end_time = time(21, 0)    # 9:00 PM

    # Case 1: Open 11:00 AM to 11:00 PM on Friday -> Should be TRUE
    open_periods = [
        {
            "open": {"day": 5, "hour": 11, "minute": 0},
            "close": {"day": 5, "hour": 23, "minute": 0},
        }
    ]
    assert is_venue_open_during_slot(open_periods, slot_date, start_time, end_time) is True

    # Case 2: Closes at 7:00 PM (19:00) -> Before end_time 21:00 -> Should be FALSE
    early_close = [
        {
            "open": {"day": 5, "hour": 11, "minute": 0},
            "close": {"day": 5, "hour": 19, "minute": 0},
        }
    ]
    assert is_venue_open_during_slot(early_close, slot_date, start_time, end_time) is False

    # Case 3: Opens at 7:00 PM (19:00) -> After start_time 18:00 -> Should be FALSE
    late_open = [
        {
            "open": {"day": 5, "hour": 19, "minute": 0},
            "close": {"day": 5, "hour": 23, "minute": 0},
        }
    ]
    assert is_venue_open_during_slot(late_open, slot_date, start_time, end_time) is False

    # Case 4: Closed on Fridays (only open Thursday: day 4) -> Should be FALSE
    wrong_day = [
        {
            "open": {"day": 4, "hour": 11, "minute": 0},
            "close": {"day": 4, "hour": 23, "minute": 0},
        }
    ]
    assert is_venue_open_during_slot(wrong_day, slot_date, start_time, end_time) is False

    # Case 5: Overnight hours (opens Friday 4:00 PM, closes Saturday 2:00 AM) -> Should be TRUE
    overnight = [
        {
            "open": {"day": 5, "hour": 16, "minute": 0},
            "close": {"day": 6, "hour": 2, "minute": 0},
        }
    ]
    assert is_venue_open_during_slot(overnight, slot_date, start_time, end_time) is True

    # Case 6: 24/7 venue (open on day 0 with no close) -> Should be TRUE
    always_open = [
        {
            "open": {"day": 0, "hour": 0, "minute": 0},
        }
    ]
    assert is_venue_open_during_slot(always_open, slot_date, start_time, end_time) is True


@pytest.mark.anyio
async def test_get_recommendations_for_poll_food_and_entertainment():
    slot_date = date(2026, 11, 13)
    start_time = time(18, 0)
    end_time = time(21, 0)

    members = [
        {
            "user_id": 1,
            "username": "alice",
            "full_name": "Alice Green",
            "lat": 34.2381,
            "lon": -118.5282,
            "max_travel_distance": 20,
        },
        {
            "user_id": 2,
            "username": "bob",
            "full_name": "Bob Blue",
            "lat": 34.1808,
            "lon": -118.3090,
            "max_travel_distance": 15,
        },
    ]

    # Food recommendations
    food_recs = await get_recommendations_for_poll(
        poll_id=10,
        group_id=1,
        category="food",
        slot_date=slot_date,
        slot_start=start_time,
        slot_end=end_time,
        members_with_coords=members,
    )
    assert food_recs["poll_id"] == 10
    assert food_recs["category"] == "food"
    assert len(food_recs["items"]) > 0
    # Every recommended place must be confirmed open during slot
    for item in food_recs["items"]:
        assert item["is_open_confirmed"] is True
        assert len(item["user_distances"]) == 2

    # Entertainment recommendations (mini golf, concerts, bowling)
    ent_recs = await get_recommendations_for_poll(
        poll_id=10,
        group_id=1,
        category="entertainment",
        slot_date=slot_date,
        slot_start=start_time,
        slot_end=end_time,
        members_with_coords=members,
    )
    assert ent_recs["category"] == "entertainment"
    assert len(ent_recs["items"]) > 0
    subcategories = [item["subcategory"] for item in ent_recs["items"]]
    assert any("Golf" in sub or "Bowling" in sub or "Concert" in sub for sub in subcategories)


def test_recommendation_endpoints_and_poll_option_addition():
    db = TestingSessionLocal()
    alice = create_user(db, "alice_rec", "alice_rec@test.com", street="100 Main St", max_dist=30)
    bob = create_user(db, "bob_rec", "bob_rec@test.com", street="200 Broadway", max_dist=20)

    group = Group(name="Weekend Explorers", owner_id=alice.id)
    db.add(group)
    db.commit()
    db.refresh(group)

    db.add_all([
        GroupMember(group_id=group.id, user_id=alice.id, role="owner"),
        GroupMember(group_id=group.id, user_id=bob.id, role="member"),
    ])

    # Shared hangout slot
    poll = HangoutPoll(
        group_id=group.id,
        date=date(2026, 11, 20),
        start_time=time(19, 0),
        end_time=time(22, 0),
        place="TBD",
    )
    db.add(poll)
    db.flush()
    db.add_all([
        PollOption(poll_id=poll.id, text="Yes", is_default=True),
        PollOption(poll_id=poll.id, text="No", is_default=True),
    ])
    db.commit()

    token_alice = create_access_token({"sub": str(alice.id), "type": "access"})

    # 1. Fetch Food Recommendations
    res_food = client.get(
        f"/api/groups/{group.id}/hangouts/{poll.id}/recommendations?category=food",
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_food.status_code == 200
    food_data = res_food.json()
    assert food_data["poll_id"] == poll.id
    assert food_data["category"] == "food"
    assert len(food_data["items"]) > 0

    # 2. Fetch Entertainment Recommendations
    res_ent = client.get(
        f"/api/groups/{group.id}/hangouts/{poll.id}/recommendations?category=entertainment",
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_ent.status_code == 200
    ent_data = res_ent.json()
    assert ent_data["category"] == "entertainment"
    assert len(ent_data["items"]) > 0

    # 3. Leader adds chosen recommendation directly to the poll options
    chosen_venue = ent_data["items"][0]["title"]
    res_add_opt = client.post(
        f"/api/groups/{group.id}/hangouts/{poll.id}/options",
        json={"text": chosen_venue},
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_add_opt.status_code == 200
    updated_poll = res_add_opt.json()
    assert any(opt["text"] == chosen_venue for opt in updated_poll["options"])

    # 4. Update poll place
    res_place = client.patch(
        f"/api/groups/{group.id}/hangouts/{poll.id}/place",
        json={"text": chosen_venue},
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_place.status_code == 200
    assert res_place.json()["place"] == chosen_venue
