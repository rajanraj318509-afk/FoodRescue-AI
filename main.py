
import streamlit as st
import pandas as pd

from food_rescue import (
    load_data,
    add_food,
    add_ngo,
    find_matches,
    create_pickup_request,
    update_request,
    seed_demo_data
)

st.set_page_config(
    page_title="FoodRescue AI",
    page_icon="🍲",
    layout="wide"
)

seed_demo_data()

st.title("🍲 FoodRescue AI")
st.subheader("Turn surplus food into a resource, not waste.")

st.write(
    "Register surplus food, discover suitable recipient "
    "organizations and coordinate pickup requests."
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "List Surplus Food",
        "Register NGO",
        "Find Matches",
        "Pickup Tracking"
    ]
)


def show_table(items):
    if items:
        st.dataframe(
            pd.DataFrame(items),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No records available yet.")


data = load_data()

if page == "Dashboard":
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Food Listings",
        len(data["food"])
    )
    col2.metric(
        "Registered NGOs",
        len(data["ngos"])
    )
    col3.metric(
        "Pickup Requests",
        len(data["requests"])
    )

    st.header("Recent Food Listings")
    show_table(data["food"][-10:])

    st.header("Recent Pickup Requests")
    show_table(data["requests"][-10:])

    st.caption(
        "Demo data is illustrative. No real donation or "
        "pickup is arranged automatically."
    )


elif page == "List Surplus Food":
    st.header("Register Surplus Food")

    with st.form("food_form"):
        name = st.text_input(
            "Food name",
            placeholder="Vegetarian meal packets"
        )

        quantity = st.number_input(
            "Quantity (meal portions)",
            min_value=1,
            value=20
        )

        location = st.text_input(
            "Pickup location",
            placeholder="Roorkee"
        )

        food_type = st.selectbox(
            "Food type",
            [
                "Cooked Meals",
                "Packaged Food",
                "Fruits",
                "Vegetables",
                "Bakery Items"
            ]
        )

        prepared_at = st.text_input(
            "Preparation time (ISO format)",
            placeholder="2026-10-24T12:00:00+00:00"
        )

        safe_until = st.text_input(
            "Pickup deadline (ISO format with timezone)",
            placeholder="2026-10-24T15:00:00+00:00"
        )

        contact = st.text_input("Contact details")

        submitted = st.form_submit_button(
            "Register Food"
        )

        if submitted:
            if not all([
                name.strip(),
                location.strip(),
                prepared_at.strip(),
                safe_until.strip(),
                contact.strip()
            ]):
                st.error("Please complete every field.")
            else:
                try:
                    item = add_food(
                        name.strip(),
                        int(quantity),
                        location.strip(),
                        food_type,
                        prepared_at.strip(),
                        safe_until.strip(),
                        contact.strip()
                    )

                    st.success(
                        f"Food listing #{item['id']} created."
                    )
                except (ValueError, OSError) as exc:
                    st.error(str(exc))

    st.subheader("All Food Listings")
    show_table(load_data()["food"])


elif page == "Register NGO":
    st.header("Register an NGO or Community Kitchen")

    with st.form("ngo_form"):
        name = st.text_input("Organization name")
        location = st.text_input("Organization location")

        capacity = st.number_input(
            "Maximum meal portions accepted",
            min_value=1,
            value=50
        )

        contact = st.text_input("Organization contact")

        submitted = st.form_submit_button(
            "Register Organization"
        )

        if submitted:
            if not all([
                name.strip(),
                location.strip(),
                contact.strip()
            ]):
                st.error("Please complete every field.")
            else:
                ngo = add_ngo(
                    name.strip(),
                    location.strip(),
                    int(capacity),
                    contact.strip()
                )

                st.success(
                    f"Organization #{ngo['id']} registered."
                )

    st.subheader("Registered Organizations")
    show_table(load_data()["ngos"])


elif page == "Find Matches":
    st.header("Find Suitable Food Recipients")

    food_items = load_data()["food"]

    if not food_items:
        st.info("Register food first.")
    else:
        food_options = {
            f"#{item['id']} — {item['name']} "
            f"({item['quantity']} portions)": item["id"]
            for item in food_items
        }

        selected_label = st.selectbox(
            "Select a food listing",
            list(food_options.keys())
        )

        food_id = food_options[selected_label]

        if st.button("Find Matching Organizations"):
            matches = find_matches(food_id)

            if matches:
                st.success(
                    f"Found {len(matches)} organizations "
                    "with sufficient listed capacity."
                )
                show_table(matches)
            else:
                st.warning(
                    "No suitable organization found. "
                    "Register an NGO or check its capacity."
                )

            st.caption(
                "Matching uses location and capacity only. "
                "It does not verify food safety or real-time availability."
            )


elif page == "Pickup Tracking":
    st.header("Pickup Requests")

    data = load_data()

    if not data["requests"]:
        st.info(
            "No pickup requests yet. Create one from a food listing."
        )
    else:
        show_table(data["requests"])

        request_options = {
            f"Request #{req['id']} — {req['status']}":
            req["id"]
            for req in data["requests"]
        }

        selected = st.selectbox(
            "Select a request to update",
            list(request_options.keys())
        )

        request_id = request_options[selected]

        new_status = st.selectbox(
            "New status",
            [
                "Confirmed",
                "Picked Up",
                "Delivered",
                "Cancelled"
            ]
        )

        if st.button("Update Request Status"):
            try:
                result = update_request(
                    request_id,
                    new_status
                )
                st.success(
                    f"Request #{result['id']} updated."
                )
            except ValueError as exc:
                st.error(str(exc))

    st.divider()
    st.subheader("Create a Pickup Request")

    data = load_data()
    available_food = [
        item for item in data["food"]
        if item["status"] == "Available"
    ]

    if available_food and data["ngos"]:
        food_options = {
            f"#{item['id']} — {item['name']}":
            item["id"]
            for item in available_food
        }

        ngo_options = {
            f"#{ngo['id']} — {ngo['name']}":
            ngo["id"]
            for ngo in data["ngos"]
        }

        food_label = st.selectbox(
            "Food listing",
            list(food_options.keys()),
            key="request_food"
        )

        ngo_label = st.selectbox(
            "Recipient organization",
            list(ngo_options.keys()),
            key="request_ngo"
        )

        if st.button("Create Pickup Request"):
            try:
                request = create_pickup_request(
                    food_options[food_label],
                    ngo_options[ngo_label]
                )

                st.success(
                    f"Request #{request['id']} created. "
                    "Recipient confirmation is still required."
                )
            except ValueError as exc:
                st.error(str(exc))
    else:
        st.info(
            "You need an available food listing and a registered "
            "organization to create a pickup request."
        )
