from urllib.parse import quote_plus


def build_google_maps_search_url(query: str) -> str:
    if not query or not query.strip():
        return ""
    encoded_query = quote_plus(query.strip())
    return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"


def build_google_maps_place_url(name: str, address: str = "") -> str:
    query = " ".join(part for part in [name, address] if part and part.strip())
    return build_google_maps_search_url(query)


def build_google_maps_lat_lng_url(latitude, longitude) -> str:
    if latitude is None or longitude is None:
        return ""
    return build_google_maps_search_url(f"{latitude},{longitude}")


def get_spot_google_maps_url(spot) -> str:
    if spot.google_maps_url:
        return spot.google_maps_url
    if spot.latitude is not None and spot.longitude is not None:
        return build_google_maps_lat_lng_url(spot.latitude, spot.longitude)
    return build_google_maps_place_url(spot.name, spot.address)


def _get_spot_value(spot, key: str, default=""):
    if isinstance(spot, dict):
        return spot.get(key, default)
    return getattr(spot, key, default)


def _build_directions_location(spot) -> str:
    latitude = _get_spot_value(spot, "latitude")
    longitude = _get_spot_value(spot, "longitude")
    if latitude not in (None, "") and longitude not in (None, ""):
        return f"{latitude},{longitude}"

    name = _get_spot_value(spot, "name")
    address = _get_spot_value(spot, "address")
    return " ".join(part for part in [name, address] if part and str(part).strip())


def build_google_maps_directions_url(spots, travelmode="driving"):
    locations = [
        _build_directions_location(spot)
        for spot in spots
        if _build_directions_location(spot)
    ]
    if len(locations) < 2:
        return ""

    origin = quote_plus(locations[0])
    destination = quote_plus(locations[-1])
    waypoints = locations[1:-1]
    url = (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={origin}"
        f"&destination={destination}"
        f"&travelmode={quote_plus(travelmode)}"
    )

    if waypoints:
        encoded_waypoints = "%7C".join(quote_plus(waypoint) for waypoint in waypoints)
        url = f"{url}&waypoints={encoded_waypoints}"

    return url
