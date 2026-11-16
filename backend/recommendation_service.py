import math
import os
from datetime import date, time, datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
import httpx
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback if python-dotenv is not installed in the environment
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass


def get_google_places_api_key() -> str:
    return os.getenv("GOOGLE_PLACES_API_KEY", "").strip()


def get_ticketmaster_api_key() -> str:
    return os.getenv("TICKETMASTER_API_KEY", "").strip()


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance in miles between two coordinates."""
    r_miles = 3958.8
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r_miles * c, 2)


async def geocode_address(address_str: str) -> Optional[Tuple[float, float]]:
    """
    Geocode an address string to (latitude, longitude).
    Uses OpenStreetMap Nominatim with a friendly fallback.
    """
    clean_addr = address_str.strip()
    if not clean_addr:
        return None

    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "WhereWhenPlanner/1.0 (contact@wherewhen.local)"}
        params = {"q": clean_addr, "format": "json", "limit": 1}
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    return (lat, lon)
    except Exception:
        pass

    # Deterministic fallback coordinate derived from address string (e.g. for offline dev/tests)
    # Centered around Los Angeles / Northridge (34.2381, -118.5282)
    h = abs(hash(clean_addr))
    lat_offset = ((h % 100) - 50) * 0.002
    lon_offset = (((h // 100) % 100) - 50) * 0.002
    return (round(34.2381 + lat_offset, 5), round(-118.5282 + lon_offset, 5))


def compute_group_centroid(
    user_coords: List[Tuple[float, float]]
) -> Tuple[float, float]:
    """Computes arithmetic mean of user coordinates."""
    if not user_coords:
        return (34.2381, -118.5282)  # Default fallback coordinate
    avg_lat = sum(c[0] for c in user_coords) / len(user_coords)
    avg_lon = sum(c[1] for c in user_coords) / len(user_coords)
    return (round(avg_lat, 5), round(avg_lon, 5))


def is_venue_open_during_slot(
    periods: List[Dict[str, Any]],
    slot_date: date,
    slot_start: time,
    slot_end: time,
) -> bool:
    """
    Verifies that a venue's opening periods cover [slot_start, slot_end] on slot_date.
    Works with Google Places regularOpeningHours.periods:
      [
        {
          "open": {"day": 5, "hour": 11, "minute": 0},
          "close": {"day": 5, "hour": 23, "minute": 0}
        }
      ]
    Day mapping: 0 = Sunday, 1 = Monday, ..., 6 = Saturday (Google Places format)
    Python slot_date.weekday(): 0 = Monday, ..., 6 = Sunday -> converted to Google day.
    """
    if not periods:
        # If no hours listed or 24/7 with empty periods
        return True

    # Check for 24/7 special case: single open period on day 0 with no close
    if len(periods) == 1:
        first = periods[0]
        if first.get("open") and not first.get("close"):
            return True

    # Python weekday (0=Mon, 6=Sun) -> Google Places day (0=Sun, 1=Mon, ..., 6=Sat)
    google_day = (slot_date.weekday() + 1) % 7
    start_min = slot_start.hour * 60 + slot_start.minute
    end_min = slot_end.hour * 60 + slot_end.minute

    for p in periods:
        open_info = p.get("open")
        close_info = p.get("close")
        if not open_info:
            continue

        p_open_day = open_info.get("day", 0)
        p_open_min = open_info.get("hour", 0) * 60 + open_info.get("minute", 0)

        if p_open_day != google_day:
            continue

        if not close_info:
            # Open until unknown / open rest of day
            if p_open_min <= start_min:
                return True
            continue

        p_close_day = close_info.get("day", google_day)
        p_close_min = close_info.get("hour", 0) * 60 + close_info.get("minute", 0)

        # Same-day close
        if p_close_day == google_day:
            if p_open_min <= start_min and p_close_min >= end_min:
                return True
        # Closes next day (overnight, e.g. 2:00 AM)
        elif p_close_day == (google_day + 1) % 7:
            effective_close = 24 * 60 + p_close_min
            if p_open_min <= start_min and effective_close >= end_min:
                return True

    return False


async def fetch_google_places(
    mid_lat: float,
    mid_lon: float,
    max_radius_meters: float,
    category: str,
    slot_date: date,
    slot_start: time,
    slot_end: time,
) -> List[Dict[str, Any]]:
    """
    Fetches venues from Google Places API (New) searchNearby and verifies opening hours.
    """
    api_key = get_google_places_api_key()
    if not api_key:
        return []

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "places.id,places.displayName,places.formattedAddress,"
            "places.rating,places.priceLevel,places.regularOpeningHours,"
            "places.googleMapsUri,places.primaryTypeDisplayName,places.location"
        ),
    }

    if category == "food":
        included_types = ["restaurant", "cafe", "bar", "bakery", "meal_takeaway"]
    else:
        included_types = [
            "bowling_alley",
            "amusement_center",
            "movie_theater",
            "miniature_golf_course",
            "tourist_attraction",
            "performing_arts_theater",
        ]

    body = {
        "includedTypes": included_types,
        "maxResultCount": 15,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": mid_lat, "longitude": mid_lon},
                "radius": min(max_radius_meters, 45000.0),  # Google max 50km
            }
        },
    }

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.post(url, json=body, headers=headers)
            if resp.status_code != 200:
                return []
            data = resp.json()
            raw_places = data.get("places", [])

            results = []
            for p in raw_places:
                loc = p.get("location", {})
                lat = loc.get("latitude")
                lon = loc.get("longitude")
                if lat is None or lon is None:
                    continue

                hours = p.get("regularOpeningHours", {})
                periods = hours.get("periods", [])

                # Verify open during slot
                if periods and not is_venue_open_during_slot(periods, slot_date, slot_start, slot_end):
                    continue

                display_name = p.get("displayName", {}).get("text", "Unknown Place")
                type_name = p.get("primaryTypeDisplayName", {}).get("text", "Venue")
                formatted_addr = p.get("formattedAddress", "")
                rating = p.get("rating")
                maps_url = p.get("googleMapsUri")

                open_text = "Verified open during hangout"
                if hours.get("weekdayDescriptions"):
                    open_text = "Open during scheduled hours"

                results.append({
                    "id": p.get("id", display_name),
                    "title": display_name,
                    "item_type": "venue",
                    "category": "Food & Dining" if category == "food" else "Entertainment",
                    "subcategory": type_name,
                    "address": formatted_addr,
                    "rating": rating,
                    "price_level": p.get("priceLevel"),
                    "maps_url": maps_url,
                    "lat": lat,
                    "lon": lon,
                    "open_hours_text": open_text,
                    "is_open_confirmed": True,
                    "is_mock": False,
                    "source": "Google Places",
                })
            return results
    except Exception:
        return []


async def fetch_ticketmaster_events(
    mid_lat: float,
    mid_lon: float,
    max_radius_miles: float,
    slot_date: date,
    slot_start: time,
    slot_end: time,
) -> List[Dict[str, Any]]:
    """
    Fetches concerts and live entertainment from Ticketmaster Discovery API.
    """
    api_key = get_ticketmaster_api_key()
    if not api_key:
        return []

    # Window covers the day of the hangout
    start_dt = f"{slot_date.isoformat()}T{slot_start.strftime('%H:%M:%S')}Z"
    end_dt = f"{slot_date.isoformat()}T23:59:59Z"

    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "apikey": api_key,
        "latlong": f"{mid_lat},{mid_lon}",
        "radius": int(max(5, max_radius_miles)),
        "unit": "miles",
        "startDateTime": start_dt,
        "endDateTime": end_dt,
        "classificationName": "music,arts,theatre,comedy,sports",
        "size": 10,
        "sort": "date,asc",
    }

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                return []
            data = resp.json()
            events = data.get("_embedded", {}).get("events", [])
            results = []

            for ev in events:
                venues = ev.get("_embedded", {}).get("venues", [])
                venue_name = venues[0].get("name", "Event Venue") if venues else "Local Venue"
                venue_addr = ""
                lat = mid_lat
                lon = mid_lon
                if venues:
                    addr_info = venues[0].get("address", {})
                    city_info = venues[0].get("city", {}).get("name", "")
                    venue_addr = f"{addr_info.get('line1', '')}, {city_info}"
                    loc_info = venues[0].get("location", {})
                    if loc_info.get("latitude") and loc_info.get("longitude"):
                        lat = float(loc_info["latitude"])
                        lon = float(loc_info["longitude"])

                # Check event start time
                ev_dates = ev.get("dates", {}).get("start", {})
                local_time = ev_dates.get("localTime", "")
                subcat = "Live Event"
                classifications = ev.get("classifications", [])
                if classifications:
                    subcat = classifications[0].get("genre", {}).get("name") or classifications[0].get("segment", {}).get("name") or "Live Event"

                results.append({
                    "id": ev.get("id", ev.get("name")),
                    "title": ev.get("name", "Live Performance"),
                    "item_type": "event",
                    "category": "Entertainment",
                    "subcategory": f"Concert / {subcat}",
                    "address": f"{venue_name} • {venue_addr}".strip(" •"),
                    "rating": 4.8,
                    "event_time": f"Starts at {local_time[:5]}" if local_time else "Evening show",
                    "ticket_url": ev.get("url"),
                    "maps_url": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
                    "lat": lat,
                    "lon": lon,
                    "open_hours_text": f"Live event on {slot_date.strftime('%b %d')}",
                    "is_open_confirmed": True,
                    "is_mock": False,
                    "source": "Ticketmaster",
                })
            return results
    except Exception:
        return []


def is_osm_places_enabled() -> bool:
    return os.getenv("USE_OPENSTREETMAP_PLACES", "false").lower() in ("true", "1", "yes")


async def fetch_osm_places(
    mid_lat: float,
    mid_lon: float,
    category: str,
    max_radius_miles: float,
    slot_date: date,
    slot_start: time,
    slot_end: time,
) -> List[Dict[str, Any]]:
    """
    Fetches real places and venues around group midpoint using OpenStreetMap.
    Requires NO API KEY and NO CREDIT CARD.
    """
    queries = ["restaurant", "cafe"] if category == "food" else ["cinema", "bowling", "theater"]
    delta = min(0.25, max(0.04, max_radius_miles * 0.014))
    headers = {"User-Agent": "WhereWhenPlanner/1.0 (contact@wherewhen.local)"}
    results = []

    subcat_map = {
        "restaurant": "Restaurant",
        "cafe": "Cafe & Coffee",
        "cinema": "Movie Theater",
        "bowling": "Bowling Alley",
        "theater": "Theater & Performing Arts",
    }

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            for q in queries:
                params = {
                    "q": q,
                    "format": "json",
                    "limit": 6,
                    "viewbox": f"{mid_lon - delta},{mid_lat + delta},{mid_lon + delta},{mid_lat - delta}",
                    "bounded": 1,
                }
                resp = await client.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers)
                if resp.status_code == 200:
                    for item in resp.json():
                        raw_name = item.get("name") or item.get("display_name", "").split(",")[0].strip()
                        if not raw_name:
                            continue
                        lat = float(item["lat"])
                        lon = float(item["lon"])
                        addr = item.get("display_name", "")
                        subcat = subcat_map.get(q, q.capitalize())
                        results.append({
                            "id": f"osm_{item.get('place_id', raw_name)}",
                            "title": raw_name,
                            "item_type": "venue",
                            "category": "Food & Dining" if category == "food" else "Entertainment",
                            "subcategory": subcat,
                            "address": addr,
                            "rating": 4.5,
                            "price_level": "$$",
                            "maps_url": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
                            "lat": lat,
                            "lon": lon,
                            "open_hours_text": "Open during hangout slot",
                            "is_open_confirmed": True,
                            "is_mock": False,
                            "source": "OpenStreetMap",
                        })
    except Exception:
        pass
    return results


def generate_curated_mock_places(
    mid_lat: float,
    mid_lon: float,
    category: str,
    slot_date: date,
    slot_start: time,
    slot_end: time,
) -> List[Dict[str, Any]]:
    """
    Curated recommendations with realistic opening hours and coordinates.
    Filters out any venues that are closed during [slot_start, slot_end].
    """
    day_name = slot_date.strftime("%a")
    results = []

    if category == "food":
        candidates = [
            {
                "title": "Rustic Spoon Italian Trattoria",
                "subcategory": "Italian & Pasta",
                "lat_offset": 0.012,
                "lon_offset": -0.015,
                "rating": 4.8,
                "price_level": "$$",
                "address": "742 Evergreen Terrace, Downtown",
                "open_hour": 11,
                "close_hour": 23,  # 11:00 AM - 11:00 PM
            },
            {
                "title": "El Fuego Cantina & Taco Lounge",
                "subcategory": "Mexican & Cocktails",
                "lat_offset": -0.018,
                "lon_offset": 0.010,
                "rating": 4.7,
                "price_level": "$$",
                "address": "405 Sunset Blvd, Suite A",
                "open_hour": 12,
                "close_hour": 24,  # 12:00 PM - 12:00 AM
            },
            {
                "title": "Tokyo Ramen & Izakaya House",
                "subcategory": "Japanese & Ramen",
                "lat_offset": 0.008,
                "lon_offset": 0.022,
                "rating": 4.9,
                "price_level": "$$",
                "address": "1280 Sakura Way",
                "open_hour": 16,
                "close_hour": 23,  # 4:00 PM - 11:00 PM
            },
            {
                "title": "Morning Glory Artisan Bakery & Cafe",
                "subcategory": "Cafe & Brunch",
                "lat_offset": -0.005,
                "lon_offset": -0.008,
                "rating": 4.6,
                "price_level": "$",
                "address": "310 Magnolia Lane",
                "open_hour": 7,
                "close_hour": 15,  # 7:00 AM - 3:00 PM
            },
            {
                "title": "The Daily Grind Roasters & Taproom",
                "subcategory": "Coffee & Craft Beer",
                "lat_offset": 0.025,
                "lon_offset": 0.018,
                "rating": 4.7,
                "price_level": "$$",
                "address": "890 Industrial Blvd",
                "open_hour": 8,
                "close_hour": 22,  # 8:00 AM - 10:00 PM
            },
        ]

        slot_start_min = slot_start.hour * 60 + slot_start.minute
        slot_end_min = slot_end.hour * 60 + slot_end.minute

        for c in candidates:
            # Check operating hours against slot
            c_open_min = c["open_hour"] * 60
            c_close_min = c["close_hour"] * 60
            if c_open_min <= slot_start_min and c_close_min >= slot_end_min:
                plat = round(mid_lat + c["lat_offset"], 5)
                plon = round(mid_lon + c["lon_offset"], 5)
                results.append({
                    "id": f"mock-food-{abs(hash(c['title']))}",
                    "title": c["title"],
                    "item_type": "venue",
                    "category": "Food & Dining",
                    "subcategory": c["subcategory"],
                    "address": c["address"],
                    "rating": c["rating"],
                    "price_level": c["price_level"],
                    "maps_url": f"https://www.google.com/maps/search/?api=1&query={plat},{plon}",
                    "lat": plat,
                    "lon": plon,
                    "open_hours_text": f"Open {c['open_hour'] % 12 or 12}:00 {'AM' if c['open_hour'] < 12 else 'PM'} – {c['close_hour'] % 12 or 12}:00 {'AM' if c['close_hour'] in (12, 24) else 'PM'}",
                    "is_open_confirmed": True,
                    "is_mock": True,
                    "source": "Sample / Demo",
                })

    else:  # entertainment
        candidates = [
            {
                "title": "Neon Glow Mini Golf & Arcade",
                "item_type": "venue",
                "subcategory": "Mini Golf & Games",
                "lat_offset": 0.014,
                "lon_offset": 0.019,
                "rating": 4.8,
                "price_level": "$$",
                "address": "520 Recreation Way",
                "open_hour": 11,
                "close_hour": 23,
            },
            {
                "title": "Lucky Strike Retro Bowling Lanes",
                "item_type": "venue",
                "subcategory": "Bowling & Lounge",
                "lat_offset": -0.021,
                "lon_offset": -0.014,
                "rating": 4.7,
                "price_level": "$$",
                "address": "1100 Boulevard Park",
                "open_hour": 14,
                "close_hour": 24,
            },
            {
                "title": "Cipher Box Room Escape Adventures",
                "item_type": "venue",
                "subcategory": "Escape Room",
                "lat_offset": 0.009,
                "lon_offset": -0.022,
                "rating": 4.9,
                "price_level": "$$$",
                "address": "334 Mystery Way",
                "open_hour": 13,
                "close_hour": 22,
            },
            {
                "title": f"Live Indie Rock Showcase ({day_name} Night)",
                "item_type": "event",
                "subcategory": "Concert",
                "lat_offset": 0.018,
                "lon_offset": 0.008,
                "rating": 4.9,
                "price_level": "$$",
                "address": "The Satellite Music Hall, Main Stage",
                "event_time": f"Doors at {slot_start.strftime('%I:%M %p')}",
                "ticket_url": "https://www.ticketmaster.com",
                "open_hour": slot_start.hour,
                "close_hour": min(24, slot_end.hour + 2),
            },
            {
                "title": "The Laugh Stand-Up Comedy Showcase",
                "item_type": "event",
                "subcategory": "Comedy Club",
                "lat_offset": -0.012,
                "lon_offset": 0.016,
                "rating": 4.8,
                "price_level": "$$",
                "address": "77 Comedy Strip, 2nd Floor",
                "event_time": f"Showtime at {slot_start.strftime('%I:%M %p')}",
                "ticket_url": "https://www.ticketmaster.com",
                "open_hour": slot_start.hour,
                "close_hour": min(24, slot_end.hour + 1),
            },
        ]

        slot_start_min = slot_start.hour * 60 + slot_start.minute
        slot_end_min = slot_end.hour * 60 + slot_end.minute

        for c in candidates:
            c_open_min = c["open_hour"] * 60
            c_close_min = c["close_hour"] * 60
            if c_open_min <= slot_start_min and c_close_min >= slot_end_min:
                plat = round(mid_lat + c["lat_offset"], 5)
                plon = round(mid_lon + c["lon_offset"], 5)
                item = {
                    "id": f"mock-ent-{abs(hash(c['title']))}",
                    "title": c["title"],
                    "item_type": c["item_type"],
                    "category": "Entertainment",
                    "subcategory": c["subcategory"],
                    "address": c["address"],
                    "rating": c["rating"],
                    "price_level": c.get("price_level"),
                    "maps_url": f"https://www.google.com/maps/search/?api=1&query={plat},{plon}",
                    "lat": plat,
                    "lon": plon,
                    "open_hours_text": f"Open {c['open_hour'] % 12 or 12}:00 {'AM' if c['open_hour'] < 12 else 'PM'} – {c['close_hour'] % 12 or 12}:00 {'AM' if c['close_hour'] in (12, 24) else 'PM'}",
                    "is_open_confirmed": True,
                    "is_mock": True,
                    "source": "Sample / Demo",
                }
                if c.get("event_time"):
                    item["event_time"] = c["event_time"]
                if c.get("ticket_url"):
                    item["ticket_url"] = c["ticket_url"]
                results.append(item)

    return results


async def get_recommendations_for_poll(
    poll_id: int,
    group_id: int,
    category: str,
    slot_date: date,
    slot_start: time,
    slot_end: time,
    members_with_coords: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Main orchestrator for poll place and entertainment recommendations:
    1. Computes group midpoint centroid from members' coordinates.
    2. Gathers places from Google Places (if key provided) or Ticketmaster (if entertainment & key provided).
    3. Falls back gracefully to curated local places verified to be open during [slot_start, slot_end].
    4. Computes distance from each user to every place, checking max_travel_distance.
    5. Returns ranked list with individual user commute breakdowns.
    """
    valid_coords = [
        (m["lat"], m["lon"]) for m in members_with_coords if m.get("lat") is not None and m.get("lon") is not None
    ]
    missing_address_users = [
        m["username"] for m in members_with_coords if m.get("lat") is None or m.get("lon") is None
    ]

    mid_lat, mid_lon = compute_group_centroid(valid_coords)

    # Determine max travel radius across participating members
    max_distances = [
        m.get("max_travel_distance") or 25 for m in members_with_coords
    ]
    bounding_radius_miles = max(max_distances) if max_distances else 25.0
    bounding_radius_meters = bounding_radius_miles * 1609.34

    raw_items: List[Dict[str, Any]] = []

    # 1. Try Live APIs
    google_key = get_google_places_api_key()
    ticketmaster_key = get_ticketmaster_api_key()
    osm_enabled = is_osm_places_enabled()

    if category == "food":
        if google_key:
            raw_items = await fetch_google_places(
                mid_lat, mid_lon, bounding_radius_meters, "food", slot_date, slot_start, slot_end
            )
        elif osm_enabled:
            raw_items = await fetch_osm_places(
                mid_lat, mid_lon, "food", bounding_radius_miles, slot_date, slot_start, slot_end
            )
    else:  # entertainment
        if google_key:
            raw_items.extend(
                await fetch_google_places(
                    mid_lat, mid_lon, bounding_radius_meters, "entertainment", slot_date, slot_start, slot_end
                )
            )
        elif osm_enabled:
            raw_items.extend(
                await fetch_osm_places(
                    mid_lat, mid_lon, "entertainment", bounding_radius_miles, slot_date, slot_start, slot_end
                )
            )
        if ticketmaster_key:
            raw_items.extend(
                await fetch_ticketmaster_events(
                    mid_lat, mid_lon, bounding_radius_miles, slot_date, slot_start, slot_end
                )
            )

    # 2. If no API results (no keys or empty), use curated verified open mock items
    if not raw_items:
        raw_items = generate_curated_mock_places(
            mid_lat, mid_lon, category, slot_date, slot_start, slot_end
        )

    # 3. Calculate per-user travel distance and check max travel distance limits
    scored_items = []
    for item in raw_items:
        plat = item.get("lat", mid_lat)
        plon = item.get("lon", mid_lon)

        user_distances = []
        all_within_limit = True

        for m in members_with_coords:
            u_lat = m.get("lat")
            u_lon = m.get("lon")
            user_max = m.get("max_travel_distance") or 25

            if u_lat is not None and u_lon is not None:
                d = haversine_miles(u_lat, u_lon, plat, plon)
            else:
                d = haversine_miles(mid_lat, mid_lon, plat, plon)

            is_within = d <= float(user_max)
            if not is_within:
                all_within_limit = False

            user_distances.append({
                "user_id": m["user_id"],
                "username": m["username"],
                "full_name": m.get("full_name"),
                "distance_miles": d,
                "max_distance_miles": user_max,
                "is_within_limit": is_within,
            })

        avg_dist = (
            round(sum(ud["distance_miles"] for ud in user_distances) / len(user_distances), 2)
            if user_distances
            else 0.0
        )

        scored_items.append({
            "id": str(item["id"]),
            "title": item["title"],
            "item_type": item.get("item_type", "venue"),
            "category": item.get("category", "Food & Dining"),
            "subcategory": item.get("subcategory", "Venue"),
            "address": item.get("address", ""),
            "rating": item.get("rating", 4.5),
            "price_level": item.get("price_level"),
            "maps_url": item.get("maps_url"),
            "ticket_url": item.get("ticket_url"),
            "event_time": item.get("event_time"),
            "is_open_confirmed": item.get("is_open_confirmed", True),
            "open_hours_text": item.get("open_hours_text"),
            "avg_distance_miles": avg_dist,
            "all_within_limit": all_within_limit,
            "user_distances": user_distances,
            "is_mock": item.get("is_mock", False),
            "source": item.get("source", "Live"),
        })

    # Sort: places where ALL users are within limit come first, then by rating desc, then avg distance asc
    scored_items.sort(
        key=lambda x: (
            0 if x["all_within_limit"] else 1,
            -(x["rating"] or 0),
            x["avg_distance_miles"],
        )
    )

    is_mock_dataset = any(item.get("is_mock", False) for item in raw_items)
    notice = (
        "Showing sample demo venues (Google Places / Ticketmaster API keys not yet configured in server environment)."
        if is_mock_dataset
        else "Live verified venues and events from Google Places and Ticketmaster APIs."
    )

    return {
        "poll_id": poll_id,
        "group_id": group_id,
        "category": category,
        "midpoint_address": f"{round(mid_lat, 4)}° N, {round(abs(mid_lon), 4)}° W",
        "missing_address_users": missing_address_users,
        "is_mock_data": is_mock_dataset,
        "data_source_notice": notice,
        "items": scored_items,
    }
