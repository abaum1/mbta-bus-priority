import streamlit as st
import helpers
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_runtime_chart(df):
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df["period"],
            x=df["best_case_runtime"],
            name="Best Case Runtime",
            orientation="h",
            marker_color="blue",
        )
    )

    fig.add_trace(
        go.Bar(
            y=df["period"],
            x=df["median_runtime"] - df["best_case_runtime"],
            name="Variable Runtime",
            orientation="h",
            marker_color="orange",
        )
    )

    fig.update_layout(
        barmode="stack",
        title=f"Fixed and Variable Runtime Comparison for {selected_route} ({selected_direction}) for {selected_intersection}",
        xaxis_title="Runtime",
        yaxis_title="period",
        template="plotly_white",
        legend_title="Runtime Type",
    )

    return fig


data = {
    "Time of Day": ["AM Peak", "Midday", "PM Peak"],
    "Direction": ["in", "out"],
    "Intersection": [
        "Broadway",
        "mtauburn",
        "s_mass_ave",
    ],
}


st.title("Evaluating MBTA Bus Priority Measures")

st.sidebar.header("Filter Options")

selected_time = st.sidebar.selectbox("Select Time of Day", data["Time of Day"])

selected_direction = st.sidebar.selectbox("Select Direction", data["Direction"])


selected_intersection = st.sidebar.selectbox(
    "Select Intersection", data["Intersection"]
)

filtered_routes = helpers.INTERSECTIONS_ROUTES[selected_intersection]

selected_route = st.sidebar.selectbox("Select Route:", options=filtered_routes)


avl_data_for_intersection = pd.read_csv(f"data/processed/{selected_intersection}.csv")

complete_trips_filtered = helpers.get_corridor_data(
    avl_data_for_intersection, selected_direction, selected_route
)

corridor_aggregated = helpers.aggregate_data_by_corridor(complete_trips_filtered)
# st.dataframe(complete_trips_filtered.head(10))
# st.dataframe(corridor_aggregated.head(10))

if (
    not complete_trips_filtered.empty
):  # TODO: need to make a new dataset that instead of by stop it is by corridor, but for individual trips.
    # st.write(
    #     f"### Corridor Runtimes for route {selected_route} ({selected_direction}) for {selected_intersection}"
    # )

    hover_columns = [
        "runtime",
        "tripdate",
        "runtime",
    ]

    fig = px.scatter(
        complete_trips_filtered,
        x="runtime",
        y="period",
        hover_data=hover_columns,
        color="period",
    )

    fig.update_traces(marker=dict(size=12, opacity=0.6))

    fig.update_layout(
        xaxis=dict(tickformat=".0f"),
        template="plotly_dark",
        title=f"Corridor Runtimes for route {selected_route} ({selected_direction}) for {selected_intersection}",
        xaxis_title="runtime",
        yaxis_title="period",
    )

    st.plotly_chart(fig)

if not corridor_aggregated.empty:

    chart = create_runtime_chart(corridor_aggregated)
    st.plotly_chart(chart, use_container_width=True)

else:
    st.warning("No data available for the selected filters.")
