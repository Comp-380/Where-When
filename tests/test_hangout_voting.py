from datetime import date, time
import pytest
from backend.auth import create_access_token, hash_password
from backend.models import User, Availability, Group, GroupMember, HangoutPoll, PollOption, PollVote
from tests.testing_db import client, TestingSessionLocal


def create_user(db, username, email, is_verified=True):
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password("Password123!"),
        is_verified=is_verified,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_hangout_polls_auto_sync_and_default_options():
    db = TestingSessionLocal()
    alice = create_user(db, "alice_h", "alice_h@test.com")
    bob = create_user(db, "bob_h", "bob_h@test.com")

    # Alice creates a group and adds Bob
    group = Group(name="Dinner Hangout Group", owner_id=alice.id)
    db.add(group)
    db.commit()
    db.refresh(group)

    db.add_all([
        GroupMember(group_id=group.id, user_id=alice.id, role="owner"),
        GroupMember(group_id=group.id, user_id=bob.id, role="member"),
    ])

    # Add overlapping availability for Friday night (18:00 - 21:00)
    d = date(2026, 11, 13)
    db.add_all([
        Availability(user_id=alice.id, date=d, start_time=time(18, 0), end_time=time(21, 0)),
        Availability(user_id=bob.id, date=d, start_time=time(18, 0), end_time=time(21, 0)),
    ])
    db.commit()

    token_alice = create_access_token({"sub": str(alice.id), "type": "access"})
    res = client.get(
        f"/api/groups/{group.id}/availability",
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["shared_slots"]) == 1
    shared_slot = data["shared_slots"][0]
    assert shared_slot["poll"] is not None

    poll = shared_slot["poll"]
    assert poll["place"] == "Dinner at a restaurant"
    assert poll["total_votes"] == 0
    assert len(poll["options"]) == 2
    option_texts = [o["text"] for o in poll["options"]]
    assert "Yes" in option_texts
    assert "No" in option_texts
    for opt in poll["options"]:
        assert opt["is_default"] is True
        assert opt["count"] == 0
        assert opt["percentage"] == 0.0


def test_hangout_voting_numbers_and_percentages():
    db = TestingSessionLocal()
    alice = create_user(db, "alice_v", "alice_v@test.com")
    bob = create_user(db, "bob_v", "bob_v@test.com")

    group = Group(name="Foodies", owner_id=alice.id)
    db.add(group)
    db.commit()
    db.refresh(group)

    db.add_all([
        GroupMember(group_id=group.id, user_id=alice.id, role="owner"),
        GroupMember(group_id=group.id, user_id=bob.id, role="member"),
    ])
    db.commit()

    # Pre-create a poll for this group
    poll = HangoutPoll(
        group_id=group.id,
        date=date(2026, 11, 14),
        start_time=time(19, 0),
        end_time=time(21, 0),
        place="Dinner at a restaurant",
    )
    db.add(poll)
    db.flush()
    opt_yes = PollOption(poll_id=poll.id, text="Yes", is_default=True)
    opt_no = PollOption(poll_id=poll.id, text="No", is_default=True)
    db.add_all([opt_yes, opt_no])
    db.commit()
    db.refresh(poll)

    token_alice = create_access_token({"sub": str(alice.id), "type": "access"})
    token_bob = create_access_token({"sub": str(bob.id), "type": "access"})

    # 1. Alice votes Yes
    res_a = client.post(
        f"/api/groups/{group.id}/hangouts/{poll.id}/vote",
        json={"option_id": opt_yes.id},
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_a.status_code == 200
    poll_data = res_a.json()
    assert poll_data["total_votes"] == 1
    assert poll_data["my_vote_option_id"] == opt_yes.id
    yes_opt = next(o for o in poll_data["options"] if o["text"] == "Yes")
    no_opt = next(o for o in poll_data["options"] if o["text"] == "No")
    assert yes_opt["count"] == 1
    assert yes_opt["percentage"] == 100.0
    assert "alice_v" in yes_opt["voters"]
    assert no_opt["count"] == 0
    assert no_opt["percentage"] == 0.0

    # 2. Bob votes No
    res_b = client.post(
        f"/api/groups/{group.id}/hangouts/{poll.id}/vote",
        json={"option_id": opt_no.id},
        headers={"Authorization": f"Bearer {token_bob}"},
    )
    assert res_b.status_code == 200
    poll_data_b = res_b.json()
    assert poll_data_b["total_votes"] == 2
    yes_opt_b = next(o for o in poll_data_b["options"] if o["text"] == "Yes")
    no_opt_b = next(o for o in poll_data_b["options"] if o["text"] == "No")
    assert yes_opt_b["count"] == 1
    assert yes_opt_b["percentage"] == 50.0
    assert no_opt_b["count"] == 1
    assert no_opt_b["percentage"] == 50.0

    # 3. Bob toggles his vote off (clicking No again)
    res_b_toggle = client.post(
        f"/api/groups/{group.id}/hangouts/{poll.id}/vote",
        json={"option_id": opt_no.id},
        headers={"Authorization": f"Bearer {token_bob}"},
    )
    assert res_b_toggle.status_code == 200
    poll_data_unvoted = res_b_toggle.json()
    assert poll_data_unvoted["total_votes"] == 1
    assert poll_data_unvoted["my_vote_option_id"] is None
    yes_opt_u = next(o for o in poll_data_unvoted["options"] if o["text"] == "Yes")
    assert yes_opt_u["count"] == 1
    assert yes_opt_u["percentage"] == 100.0


def test_leader_can_add_and_delete_custom_option():
    db = TestingSessionLocal()
    alice = create_user(db, "alice_ldr", "alice_ldr@test.com")
    bob = create_user(db, "bob_ldr", "bob_ldr@test.com")

    group = Group(name="Leader Options Group", owner_id=alice.id)
    db.add(group)
    db.commit()
    db.refresh(group)

    db.add_all([
        GroupMember(group_id=group.id, user_id=alice.id, role="owner"),
        GroupMember(group_id=group.id, user_id=bob.id, role="member"),
    ])

    poll = HangoutPoll(
        group_id=group.id,
        date=date(2026, 11, 15),
        start_time=time(18, 0),
        end_time=time(20, 0),
        place="Dinner at a restaurant",
    )
    db.add(poll)
    db.flush()
    db.add_all([
        PollOption(poll_id=poll.id, text="Yes", is_default=True),
        PollOption(poll_id=poll.id, text="No", is_default=True),
    ])
    db.commit()

    token_alice = create_access_token({"sub": str(alice.id), "type": "access"})
    token_bob = create_access_token({"sub": str(bob.id), "type": "access"})

    # Bob (regular member) attempts to add option -> 403 Forbidden
    res_fail = client.post(
        f"/api/groups/{group.id}/hangouts/{poll.id}/options",
        json={"text": "Maybe"},
        headers={"Authorization": f"Bearer {token_bob}"},
    )
    assert res_fail.status_code == 403

    # Alice (group leader) adds custom option "Maybe"
    res_add = client.post(
        f"/api/groups/{group.id}/hangouts/{poll.id}/options",
        json={"text": "Maybe"},
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_add.status_code == 200
    poll_data = res_add.json()
    assert len(poll_data["options"]) == 3
    maybe_opt = next(o for o in poll_data["options"] if o["text"] == "Maybe")
    assert maybe_opt["is_default"] is False

    # Cannot delete default option (Yes/No)
    yes_opt = next(o for o in poll_data["options"] if o["text"] == "Yes")
    res_del_fail = client.delete(
        f"/api/groups/{group.id}/hangouts/{poll.id}/options/{yes_opt["id"]}",
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_del_fail.status_code == 400

    # Alice deletes custom option "Maybe"
    res_del = client.delete(
        f"/api/groups/{group.id}/hangouts/{poll.id}/options/{maybe_opt['id']}",
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_del.status_code == 200
    poll_after_del = res_del.json()
    assert len(poll_after_del["options"]) == 2


def test_group_poll_options_apply_to_all_current_and_future_polls():
    db = TestingSessionLocal()
    alice = create_user(db, "alice_grp_opt", "alice_grp_opt@test.com")
    bob = create_user(db, "bob_grp_opt", "bob_grp_opt@test.com")

    group = Group(name="Weekend Hangout Circle", owner_id=alice.id)
    db.add(group)
    db.commit()
    db.refresh(group)

    db.add_all([
        GroupMember(group_id=group.id, user_id=alice.id, role="owner"),
        GroupMember(group_id=group.id, user_id=bob.id, role="member"),
    ])

    # 1. Initially create two overlapping availability slots
    d1 = date(2026, 11, 20)
    d2 = date(2026, 11, 21)
    db.add_all([
        Availability(user_id=alice.id, date=d1, start_time=time(18, 0), end_time=time(20, 0)),
        Availability(user_id=bob.id, date=d1, start_time=time(18, 0), end_time=time(20, 0)),
        Availability(user_id=alice.id, date=d2, start_time=time(18, 0), end_time=time(20, 0)),
        Availability(user_id=bob.id, date=d2, start_time=time(18, 0), end_time=time(20, 0)),
    ])
    db.commit()

    token_alice = create_access_token({"sub": str(alice.id), "type": "access"})
    token_bob = create_access_token({"sub": str(bob.id), "type": "access"})

    # Check availability to trigger initial poll generation for both slots
    res_avail = client.get(
        f"/api/groups/{group.id}/availability",
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_avail.status_code == 200
    assert len(res_avail.json()["polls"]) == 2

    # 2. Check group poll options endpoint
    res_opts = client.get(
        f"/api/groups/{group.id}/poll-options",
        headers={"Authorization": f"Bearer {token_bob}"},
    )
    assert res_opts.status_code == 200
    options = res_opts.json()
    assert len(options) == 2
    assert [o["text"] for o in options] == ["Yes", "No"]

    # 3. Bob (non-leader) cannot add group option
    res_bob_add = client.post(
        f"/api/groups/{group.id}/poll-options",
        json={"text": "Drinks instead"},
        headers={"Authorization": f"Bearer {token_bob}"},
    )
    assert res_bob_add.status_code == 403

    # 4. Alice (leader) adds option in the Groups tab for all polls
    res_alice_add = client.post(
        f"/api/groups/{group.id}/poll-options",
        json={"text": "Drinks instead"},
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_alice_add.status_code == 200
    updated_group_opts = res_alice_add.json()
    assert len(updated_group_opts) == 3
    drinks_opt = next(o for o in updated_group_opts if o["text"] == "Drinks instead")
    assert drinks_opt["is_default"] is False

    # Verify that BOTH existing polls now contain "Drinks instead"
    res_hangouts = client.get(
        f"/api/groups/{group.id}/hangouts",
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_hangouts.status_code == 200
    current_polls = res_hangouts.json()
    assert len(current_polls) == 2
    for p in current_polls:
        assert any(o["text"] == "Drinks instead" for o in p["options"])

    # 5. Future polls automatically inherit "Drinks instead"
    d3 = date(2026, 11, 22)
    db.add_all([
        Availability(user_id=alice.id, date=d3, start_time=time(19, 0), end_time=time(21, 0)),
        Availability(user_id=bob.id, date=d3, start_time=time(19, 0), end_time=time(21, 0)),
    ])
    db.commit()

    res_avail2 = client.get(
        f"/api/groups/{group.id}/availability",
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_avail2.status_code == 200
    all_polls = res_avail2.json()["polls"]
    assert len(all_polls) == 3
    # Check the new 3rd poll
    poll_d3 = next(p for p in all_polls if p["date"] == "2026-11-22")
    assert any(o["text"] == "Drinks instead" for o in poll_d3["options"])

    # 6. Cannot delete default options
    yes_group_opt = next(o for o in updated_group_opts if o["text"] == "Yes")
    res_del_def = client.delete(
        f"/api/groups/{group.id}/poll-options/{yes_group_opt['id']}",
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_del_def.status_code == 400

    # 7. Alice deletes "Drinks instead" from group options
    res_del_custom = client.delete(
        f"/api/groups/{group.id}/poll-options/{drinks_opt['id']}",
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    assert res_del_custom.status_code == 200
    assert len(res_del_custom.json()) == 2

    # Verify "Drinks instead" is deleted from all polls
    res_hangouts_after = client.get(
        f"/api/groups/{group.id}/hangouts",
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    for p in res_hangouts_after.json():
        assert not any(o["text"] == "Drinks instead" for o in p["options"])


def test_websocket_realtime_broadcast():
    db = TestingSessionLocal()
    alice = create_user(db, "alice_ws", "alice_ws@test.com")
    bob = create_user(db, "bob_ws", "bob_ws@test.com")

    group = Group(name="WebSocket Group", owner_id=alice.id)
    db.add(group)
    db.commit()
    db.refresh(group)

    db.add_all([
        GroupMember(group_id=group.id, user_id=alice.id, role="owner"),
        GroupMember(group_id=group.id, user_id=bob.id, role="member"),
    ])

    poll = HangoutPoll(
        group_id=group.id,
        date=date(2026, 11, 16),
        start_time=time(19, 0),
        end_time=time(21, 0),
        place="Dinner at a restaurant",
    )
    db.add(poll)
    db.flush()
    opt_yes = PollOption(poll_id=poll.id, text="Yes", is_default=True)
    opt_no = PollOption(poll_id=poll.id, text="No", is_default=True)
    db.add_all([opt_yes, opt_no])
    db.commit()
    db.refresh(poll)

    token_alice = create_access_token({"sub": str(alice.id), "type": "access"})
    token_bob = create_access_token({"sub": str(bob.id), "type": "access"})

    with client.websocket_connect(f"/ws/groups/{group.id}?token={token_bob}") as ws_bob:
        # Alice votes Yes via REST API
        res = client.post(
            f"/api/groups/{group.id}/hangouts/{poll.id}/vote",
            json={"option_id": opt_yes.id},
            headers={"Authorization": f"Bearer {token_alice}"},
        )
        assert res.status_code == 200

        # Bob receives the real-time update over WebSocket instantly!
        data = ws_bob.receive_json()
        assert data["type"] == "POLL_UPDATED"
        poll_info = data["poll"]
        assert poll_info["id"] == poll.id
        assert poll_info["total_votes"] == 1
        yes_opt = next(o for o in poll_info["options"] if o["text"] == "Yes")
        assert yes_opt["count"] == 1
        assert yes_opt["percentage"] == 100.0
