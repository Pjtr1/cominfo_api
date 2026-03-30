import math

def haversine(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2*math.asin(math.sqrt(a))
    r = 6371  # Radius of Earth in km
    return round(c * r, 2)  # rounded to 2 decimals

# services/serializer.py
def serialize_for_llm(obj, user_lat=None, user_lon=None):
    """
    Serialize SQLAlchemy objects for LLM context:
    - Ignore unnecessary fields (image_url, payment_qr_url, owner_id)
    - Include useful fields only if they are not None
    - Replace latitude/longitude with distance_km from user
    """
    import math

    def haversine(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371
        return round(c * r, 2)

    if isinstance(obj, list):
        return [serialize_for_llm(o, user_lat, user_lon) for o in obj]

    if hasattr(obj, "__table__"):
        always_ignore_fields = {"image_url", "payment_qr_url", "owner_id"}
        allowed_fields = {
            "Canteen": ["id", "name", "utilization", "latitude", "longitude"],
            "Restaurant": ["id", "name", "utilization", "is_open", "canteen_id", "latitude", "longitude"]
        }

        cls_name = obj.__class__.__name__
        fields = allowed_fields.get(cls_name, [])

        data = {}
        for k in fields:
            if k in always_ignore_fields:
                continue
            value = getattr(obj, k)
            if value is not None:
                data[k] = value

        # compute distance if lat/lon exist and user coordinates provided
        if user_lat is not None and user_lon is not None:
            lat = getattr(obj, "latitude", None)
            lon = getattr(obj, "longitude", None)
            if lat is not None and lon is not None:
                data["distance_km"] = haversine(user_lat, user_lon, lat, lon)
                data.pop("latitude", None)
                data.pop("longitude", None)

        return data

    return obj
