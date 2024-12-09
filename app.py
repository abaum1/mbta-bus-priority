import streamlit as st
from helpers import get_intersection_data

data = {
    "Time of Day": ["AM Peak", "Midday", "PM Peak"],
    "Direction": ["in", "out"],
    "Intersection": [
        "Broadway",
        "mtauburn",
        "s_mass_ave",
    ],
}

intersections_routes = {
    "Broadway": [89, 101],
    "mtauburn": [71, 73],
    "s_mass_ave": [1],
}

st.title("Evaluating MBTA Bus Priority Measures")

st.sidebar.header("Filter Options")

selected_time = st.sidebar.selectbox("Select Time of Day", data["Time of Day"])

selected_direction = st.sidebar.selectbox("Select Direction", data["Direction"])


selected_intersection = st.sidebar.selectbox(
    "Select Intersection", data["Intersection"]
)

filtered_routes = intersections_routes[selected_intersection]

selected_route = st.sidebar.selectbox("Select Route:", options=filtered_routes)

intersection_data = get_intersection_data(
    selected_intersection, selected_direction, selected_route
)
st.dataframe(intersection_data.head(10))

# st.subheader("Selected Filters:")
# st.write(f"**Time of Day:** {selected_time}")
# st.write(f"**Direction:** {selected_direction}")
# st.write(f"**Intersection:** {selected_intersection}")

# st.subheader("Filtered Results:")
# st.write("Use the selected filters to query your dataset.")
