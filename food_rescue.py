
import json
import os
from datetime import datetime, timedelta, timezone

DATA_FILE = "food_data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"food": [], "ngos": [], "requests": []}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except (json.JSONDecodeError, OSError):
        return {"food": [], "ngos": [], "requests": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def add_food(name, quantity, location, food_type, prepared_at,
             safe_until, contact):
    data = load_data()

    item = {
        "id": len(data["food"]) + 1,
        "name": name,
        "quantity": quantity,
        "location": location,
        "food_type": food_type,
        "prepared_at": prepared_at,
        "safe_until": safe_until,
        "contact": contact,
        "status": "Available"
    }

    data["food"].append(item)
    save_data(data)
    return item


def add_ngo(name, location, capacity, contact):
    data = load_data()

    ngo = {
        "id": len(data["ngos"]) + 1,
        "name": name,
        "location": location,
        "capacity": capacity,
        "contact": contact
    }

    data["ngos"].append(ngo)
    save_data(data)
    return ngo


def find_matches(food_id):
    data = load_data()
    food = next(
        (item for item in data["food"]
         if item["id"] == food_id),
        None
    )

    if not food:
        return []

    matches = []

    for ngo in data["ngos"]:
        if ngo["capacity"] >= food["quantity"]:
            same_location = (
                ngo["location"].strip().lower()
                == food["location"].strip().lower()
            )

            matches.append({
                **ngo,
                "same_location": same_location
            })

    matches.sort(
        key=lambda ngo: (
            not ngo["same_location"],
            ngo["name"]
        )
    )

    return matches


def create_pickup_request(food_id, ngo_id):
    data = load_data()

    food = next(
        (item for item in data["food"]
         if item["id"] == food_id),
        None
    )

    ngo = next(
        (item for item in data["ngos"]
         if item["id"] == ngo_id),
        None
    )

    if not food or not ngo:
        raise ValueError("Food listing or NGO not found.")

    if food["status"] != "Available":
        raise ValueError("This food is no longer available.")

    if ngo["capacity"] < food["quantity"]:
        raise ValueError("NGO capacity is insufficient.")

    try:
        deadline = datetime.fromisoformat(food["safe_until"])
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if deadline <= datetime.now(timezone.utc):
            raise ValueError("Food pickup deadline has passed.")
    except ValueError as exc:
        raise ValueError(
            "Invalid or expired safety deadline: " + str(exc)
        ) from exc

    request_id = len(data["requests"]) + 1

    request = {
        "id": request_id,
        "food_id": food_id,
        "ngo_id": ngo_id,
        "status": "Pending Confirmation",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    data["requests"].append(request)
    food["status"] = "Pickup Requested"

    save_data(data)
    return request


def update_request(request_id, new_status):
    allowed = {
        "Confirmed",
        "Picked Up",
        "Delivered",
        "Cancelled"
    }

    if new_status not in allowed:
        raise ValueError("Invalid status.")

    data = load_data()

    request = next(
        (item for item in data["requests"]
         if item["id"] == request_id),
        None
    )

    if not request:
        raise ValueError("Request not found.")

    request["status"] = new_status

    food = next(
        (item for item in data["food"]
         if item["id"] == request["food_id"]),
        None
    )

    if food:
        if new_status == "Cancelled":
            food["status"] = "Available"
        elif new_status == "Delivered":
            food["status"] = "Rescued"

    save_data(data)
    return request


def seed_demo_data():
    data = load_data()

    if data["food"] or data["ngos"]:
        return

    deadline = (
        datetime.now(timezone.utc) + timedelta(hours=3)
    ).isoformat()

    add_ngo(
        "Demo Community Kitchen",
        "Roorkee",
        100,
        "demo@example.com"
    )

    add_food(
        "Fresh vegetarian meal packets",
        20,
        "Roorkee",
        "Cooked Meals",
        datetime.now(timezone.utc).isoformat(),
        deadline,
        "canteen@example.com"
    )
