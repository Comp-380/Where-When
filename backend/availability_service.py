from datetime import date, time
from typing import Dict, List, Tuple, Any, Optional


def time_to_minutes(t: time) -> int:
    """Converts a datetime.time to minutes since midnight."""
    return t.hour * 60 + t.minute


def minutes_to_time(m: int) -> time:
    """Converts minutes since midnight to a datetime.time."""
    m = max(0, min(m, 24 * 60 - 1))
    return time(hour=m // 60, minute=m % 60)


def merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Sorts and merges overlapping or adjacent [start, end] intervals.
    Example: [(600, 720), (720, 840)] -> [(600, 840)]
    """
    if not intervals:
        return []
    
    # Sort primarily by start time, secondarily by end time
    sorted_intervals = sorted(intervals, key=lambda x: (x[0], x[1]))
    merged: List[Tuple[int, int]] = [sorted_intervals[0]]

    for start, end in sorted_intervals[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:  # Overlapping or adjacent
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))

    return merged


def compute_mutual_intervals(
    user_intervals: Dict[str, List[Tuple[int, int]]],
    total_group_members: int,
) -> Dict[str, Any]:
    """
    Given a mapping of user_identifier -> list of (start_min, end_min) intervals,
    computes:
      - shared_slots: intervals where ALL active members in the group are free.
      - partial_slots: intervals where at least 2 members are free (if total members > 1).
    """
    if not user_intervals or total_group_members <= 0:
        return {"shared_slots": [], "partial_slots": []}

    # First, merge intervals for each individual user
    normalized_users: Dict[str, List[Tuple[int, int]]] = {}
    boundaries_set = set()

    for user_id, intervals in user_intervals.items():
        merged = merge_intervals(intervals)
        normalized_users[user_id] = merged
        for start, end in merged:
            boundaries_set.add(start)
            boundaries_set.add(end)

    if not boundaries_set:
        return {"shared_slots": [], "partial_slots": []}

    boundaries = sorted(list(boundaries_set))
    raw_segments: List[Dict[str, Any]] = []

    # Partition the timeline into discrete slices between consecutive boundaries
    for i in range(len(boundaries) - 1):
        seg_start = boundaries[i]
        seg_end = boundaries[i + 1]
        if seg_start >= seg_end:
            continue

        active_users = []
        for user_id, intervals in normalized_users.items():
            # Check if this user covers [seg_start, seg_end]
            for u_start, u_end in intervals:
                if u_start <= seg_start and seg_end <= u_end:
                    active_users.append(user_id)
                    break

        if active_users:
            raw_segments.append({
                "start": seg_start,
                "end": seg_end,
                "users": sorted(active_users),
                "count": len(active_users),
            })

    # Helper to merge contiguous segments with identical active user sets
    def collapse_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not segments:
            return []
        collapsed = [segments[0]]
        for seg in segments[1:]:
            prev = collapsed[-1]
            if prev["end"] == seg["start"] and prev["users"] == seg["users"]:
                prev["end"] = seg["end"]
            else:
                collapsed.append(seg)
        return collapsed

    # 1. Exact match where EVERY member in the group is free
    everyone_segments = [
        {"start": s["start"], "end": s["end"], "users": s["users"], "count": s["count"]}
        for s in raw_segments
        if s["count"] == total_group_members
    ]
    collapsed_everyone = collapse_segments(everyone_segments)

    # 2. Partial common slots (where at least 2 members are free, or 1 if group has 1 member)
    min_count = 2 if total_group_members > 1 else 1
    partial_segments = [
        {"start": s["start"], "end": s["end"], "users": s["users"], "count": s["count"]}
        for s in raw_segments
        if s["count"] >= min_count
    ]
    collapsed_partial = collapse_segments(partial_segments)

    return {
        "shared_slots": collapsed_everyone,
        "partial_slots": collapsed_partial,
    }
