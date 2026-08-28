import streamlit as st
import pandas as pd
import os


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Train Enquiry System",
    page_icon="🚆",
    layout="wide"
)


# ==================================================
# FILE PATHS
# ==================================================

BASE_DIR = os.path.dirname(__file__)

DATA_PATH = os.path.join(
    BASE_DIR,
    "..",
    "data",
    "train_cleaned.csv"
)

SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "..",
    "outputs",
    "tables",
    "train_summary.csv"
)

STOPS_PATH = os.path.join(
    BASE_DIR,
    "..",
    "outputs",
    "tables",
    "train_stop_analysis.csv"
)


# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_csv(DATA_PATH)
train_summary = pd.read_csv(SUMMARY_PATH)
train_stops = pd.read_csv(STOPS_PATH)


# ==================================================
# SESSION STATE
# ==================================================

if "search_results" not in st.session_state:
    st.session_state.search_results = None

if "last_source" not in st.session_state:
    st.session_state.last_source = None

if "last_destination" not in st.session_state:
    st.session_state.last_destination = None


# ==================================================
# PAGE HEADER
# ==================================================

st.title("🚆 Train Enquiry System")

st.write(
    "Search for direct trains between two stations."
)


# ==================================================
# SUMMARY METRICS
# ==================================================

total_trains = df["Train_No"].nunique()
total_stations = df["Station_Name"].nunique()

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Total Trains",
        f"{total_trains:,}"
    )

with col2:
    st.metric(
        "Total Stations",
        f"{total_stations:,}"
    )

st.divider()


# ==================================================
# STATION LIST
# ==================================================

stations = sorted(
    df["Station_Name"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


# ==================================================
# SEARCH SECTION
# ==================================================

st.subheader("🔎 Search Trains")

with st.form("train_search_form"):

    col1, col2 = st.columns(2)

    with col1:
        source_station = st.selectbox(
            "Source Station",
            stations,
            key="source_station"
        )

    with col2:
        destination_station = st.selectbox(
            "Destination Station",
            stations,
            key="destination_station"
        )

    search_button = st.form_submit_button(
        "🔍 Search Trains",
        use_container_width=True
    )


# ==================================================
# SEARCH LOGIC
# ==================================================

if search_button:

    # Reset filters whenever a new search is performed.
    st.session_state.pop("route_type_filter", None)
    st.session_state.pop("max_stops_filter", None)
    st.session_state.pop("sort_results", None)

    if source_station == destination_station:

        st.warning(
            "Source and destination stations cannot be the same."
        )

        st.session_state.search_results = None

    else:

        # ------------------------------------------------
        # SOURCE STATION DATA
        # ------------------------------------------------

        source_data = df[
            df["Station_Name"] == source_station
        ][
            [
                "Train_No",
                "SN",
                "Departure_Time",
                "Distance"
            ]
        ].copy()

        source_data = source_data.rename(
            columns={
                "SN": "Source_SN",
                "Departure_Time": "Source_Departure",
                "Distance": "Source_Distance"
            }
        )

        source_data = source_data.drop_duplicates(
            subset=["Train_No"]
        )


        # ------------------------------------------------
        # DESTINATION STATION DATA
        # ------------------------------------------------

        destination_data = df[
            df["Station_Name"] == destination_station
        ][
            [
                "Train_No",
                "SN",
                "Arrival_time",
                "Distance"
            ]
        ].copy()

        destination_data = destination_data.rename(
            columns={
                "SN": "Destination_SN",
                "Arrival_time": "Destination_Arrival",
                "Distance": "Destination_Distance"
            }
        )

        destination_data = destination_data.drop_duplicates(
            subset=["Train_No"]
        )


        # ------------------------------------------------
        # MATCH TRAINS
        # ------------------------------------------------

        matched_trains = pd.merge(
            source_data,
            destination_data,
            on="Train_No",
            how="inner"
        )


        # ------------------------------------------------
        # CHECK STATION ORDER
        # ------------------------------------------------

        direct_trains = matched_trains[
            matched_trains["Source_SN"]
            <
            matched_trains["Destination_SN"]
        ].copy()


        # ------------------------------------------------
        # CONVERT TIMES
        # ------------------------------------------------

        direct_trains["Source_Departure"] = pd.to_datetime(
            direct_trains["Source_Departure"],
            errors="coerce"
        )

        direct_trains["Destination_Arrival"] = pd.to_datetime(
            direct_trains["Destination_Arrival"],
            errors="coerce"
        )


        # ------------------------------------------------
        # REMOVE MISSING TIMES
        # ------------------------------------------------

        direct_trains = direct_trains.dropna(
            subset=[
                "Source_Departure",
                "Destination_Arrival"
            ]
        ).copy()


        # ------------------------------------------------
        # CALCULATE JOURNEY DURATION
        # ------------------------------------------------

        direct_trains["Journey_Duration"] = (
            direct_trains["Destination_Arrival"]
            -
            direct_trains["Source_Departure"]
        )


        # ------------------------------------------------
        # HANDLE OVERNIGHT JOURNEYS
        # ------------------------------------------------

        overnight_mask = (
            direct_trains["Journey_Duration"]
            < pd.Timedelta(0)
        )

        direct_trains.loc[
            overnight_mask,
            "Journey_Duration"
        ] = (
            direct_trains.loc[
                overnight_mask,
                "Journey_Duration"
            ]
            +
            pd.Timedelta(days=1)
        )


        # ------------------------------------------------
        # CONVERT DURATION TO HOURS
        # ------------------------------------------------

        direct_trains["Journey_Duration_Hours"] = (
            direct_trains["Journey_Duration"]
            .dt.total_seconds()
            / 3600
        )


        # ------------------------------------------------
        # REMOVE INVALID DURATIONS
        # ------------------------------------------------

        direct_trains = direct_trains[
            direct_trains["Journey_Duration_Hours"].notna()
            &
            (
                direct_trains["Journey_Duration_Hours"] >= 0
            )
        ].copy()


        # ------------------------------------------------
        # CALCULATE SOURCE-TO-DESTINATION DISTANCE
        # ------------------------------------------------

        direct_trains["Distance"] = (
            direct_trains["Destination_Distance"]
            -
            direct_trains["Source_Distance"]
        )


        # ------------------------------------------------
        # GET ROUTE TYPE
        # ------------------------------------------------

        route_details = train_summary[
            [
                "Train_No",
                "Route_Type"
            ]
        ].drop_duplicates(
            subset=["Train_No"]
        )

        direct_trains = direct_trains.merge(
            route_details,
            on="Train_No",
            how="left"
        )


        # ------------------------------------------------
        # GET NUMBER OF STOPS
        # ------------------------------------------------

        stops_details = train_stops[
            [
                "Train_No",
                "Number_of_Stops"
            ]
        ].drop_duplicates(
            subset=["Train_No"]
        )

        direct_trains = direct_trains.merge(
            stops_details,
            on="Train_No",
            how="left"
        )


        # ------------------------------------------------
        # FORMAT DEPARTURE TIME
        # ------------------------------------------------

        direct_trains["Departure"] = (
            direct_trains["Source_Departure"]
            .dt.strftime("%H:%M")
        )


        # ------------------------------------------------
        # FORMAT ARRIVAL TIME
        # ------------------------------------------------

        direct_trains["Arrival"] = (
            direct_trains["Destination_Arrival"]
            .dt.strftime("%H:%M")
        )


        # ------------------------------------------------
        # FORMAT JOURNEY DURATION
        # ------------------------------------------------

        def format_duration(hours):

            if pd.isna(hours):
                return "N/A"

            total_minutes = int(
                round(float(hours) * 60)
            )

            hours_part = total_minutes // 60
            minutes_part = total_minutes % 60

            return f"{hours_part}h {minutes_part}m"


        direct_trains["Duration"] = (
            direct_trains["Journey_Duration_Hours"]
            .apply(format_duration)
        )


        # ------------------------------------------------
        # CREATE FINAL RESULT TABLE
        # ------------------------------------------------

        results = direct_trains[
            [
                "Train_No",
                "Departure",
                "Arrival",
                "Duration",
                "Journey_Duration_Hours",
                "Distance",
                "Route_Type",
                "Number_of_Stops"
            ]
        ].copy()


        results = results.rename(
            columns={
                "Train_No": "Train Number",
                "Duration": "Journey Duration",
                "Distance": "Distance (km)",
                "Route_Type": "Route Type",
                "Number_of_Stops": "Stops"
            }
        )


        # ------------------------------------------------
        # SAVE RESULTS
        # ------------------------------------------------

        st.session_state.search_results = results.copy()
        st.session_state.last_source = source_station
        st.session_state.last_destination = destination_station


# ==================================================
# DISPLAY SEARCH RESULTS
# ==================================================

if st.session_state.search_results is not None:

    results = st.session_state.search_results.copy()

    source_station = st.session_state.last_source
    destination_station = st.session_state.last_destination


    # ------------------------------------------------
    # ROUTE TYPE FILTER
    # ------------------------------------------------

    route_types = [
        "Short",
        "Medium",
        "Long"
    ]

    available_route_types = [
        route_type
        for route_type in route_types
        if route_type in results["Route Type"].dropna().unique()
    ]

    if available_route_types:

        selected_route_types = st.multiselect(
            "Filter by Route Type",
            available_route_types,
            default=available_route_types,
            key="route_type_filter"
        )

        if selected_route_types:

            results = results[
                results["Route Type"].isin(
                    selected_route_types
                )
            ].copy()

        else:

            results = results.iloc[0:0].copy()

    else:

        selected_route_types = []

        if results.empty:
            st.info(
                "No direct trains are available for this route."
            )


    # ------------------------------------------------
    # MAXIMUM STOPS FILTER
    # ------------------------------------------------

    if not results.empty:

        stops_numeric = pd.to_numeric(
            results["Stops"],
            errors="coerce"
        )

        results["Stops"] = stops_numeric

        results = results.dropna(
            subset=["Stops"]
        ).copy()

        if not results.empty:

            min_stops = int(
                results["Stops"].min()
            )

            max_stops = int(
                results["Stops"].max()
            )

            selected_max_stops = st.slider(
                "Maximum Number of Stops",
                min_value=min_stops,
                max_value=max_stops,
                value=max_stops,
                step=1,
                key="max_stops_filter"
            )

            results = results[
                results["Stops"] <= selected_max_stops
            ].copy()


    # ------------------------------------------------
    # SORT RESULTS
    # ------------------------------------------------

    sort_option = st.selectbox(
        "Sort Results By",
        [
            "Departure Time",
            "Journey Duration",
            "Distance"
        ],
        key="sort_results"
    )


    if sort_option == "Departure Time":

        results = results.sort_values(
            by="Departure"
        )


    elif sort_option == "Journey Duration":

        results = results.sort_values(
            by="Journey_Duration_Hours"
        )


    elif sort_option == "Distance":

        results = results.sort_values(
            by="Distance (km)"
        )


    # ------------------------------------------------
    # SEARCH SUMMARY
    # ------------------------------------------------

    if len(results) > 0:

        st.success(
            f"{len(results)} train(s) found "
            f"from {source_station} to "
            f"{destination_station}."
        )

    else:

        st.warning(
            f"No trains match the selected filters "
            f"for {source_station} to "
            f"{destination_station}."
        )


    # ------------------------------------------------
    # AVAILABLE TRAINS
    # ------------------------------------------------

    st.subheader("🚆 Available Trains")


    display_results = results[
        [
            "Train Number",
            "Departure",
            "Arrival",
            "Journey Duration",
            "Distance (km)",
            "Route Type",
            "Stops"
        ]
    ].copy()


    # Show stops as integers instead of 3.0, 8.0, etc.
    if not display_results.empty:
        display_results["Stops"] = (
            display_results["Stops"]
            .astype(int)
        )


    st.dataframe(
        display_results,
        use_container_width=True,
        hide_index=True
    )
