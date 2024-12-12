import streamlit as st
import helpers
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_runtime_chart(df):
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df["evaluation_period"],
            x=df["best_case_runtime"],
            name="Best Case Runtime",
            orientation="h",
            marker_color="green",
        )
    )

    fig.add_trace(
        go.Bar(
            y=df["evaluation_period"],
            x=df["median_runtime"] - df["best_case_runtime"],
            name="Variable Runtime",
            orientation="h",
            marker_color="purple",
        )
    )

    fig.update_layout(
        barmode="stack",
        title=f"Fixed and Variable Runtime Comparison for {selected_route} ({selected_direction}) for {selected_intersection}, {selected_tod}",
        xaxis_title="Runtime",
        yaxis_title="evaluation_period",
        template="plotly_white",
        legend_title="Runtime Type",
    )

    return fig


data = {
    "Time of Day": ["AM Peak", "Midday", "PM Peak"],
    "Direction": ["in", "out"],
    "Intersection": [
        "Broadway",
        "Belmont_Mt. Auburn",
    ],
}


st.title("Evaluating MBTA Bus Priority Measures")

st.sidebar.header("Filter Options")

selected_tod = st.sidebar.selectbox("Select Time of Day", data["Time of Day"])

selected_direction = st.sidebar.selectbox("Select Direction", data["Direction"])


selected_intersection = st.sidebar.selectbox(
    "Select Intersection", data["Intersection"]
)

filtered_routes = helpers.INTERSECTIONS_ROUTES[selected_intersection]

selected_route = st.sidebar.selectbox("Select Route:", options=filtered_routes)


avl_data_for_intersection = pd.read_csv(f"processed_data/{selected_intersection}.csv")


avl_data_filtered = helpers.filter_data_by_tod_route_direction(
    avl_data_for_intersection, selected_route, selected_direction, selected_tod
)


# calculate CoV Hwy
result = (
    avl_data_filtered.groupby(
        [
            "evaluation_period",
            "stopid",
        ]
    )["headway"]
    .apply(helpers.calculate_cv)
    .reset_index(name="hwy_cv")
)


if not result.empty:

    result_nonan = result.dropna(subset=["hwy_cv"], inplace=False)
    result_nonan["stopid"] = result_nonan["stopid"].astype(str)

    result["stopid"] = pd.Categorical(
        result["stopid"],
        categories=helpers.STOP_SEQUENCES[selected_intersection][selected_route][
            selected_direction
        ],
        ordered=True,
    )

    fig = px.scatter(
        result_nonan,
        x="hwy_cv",
        y="stopid",
        color="evaluation_period",
        color_discrete_map={"before": "blue", "after": "red"},
        labels={"cov_hwy": "Coefficient of Variation (CV)", "stopid": "Stop ID"},
        title="Scatterplot of CV vs Stop ID",
    )

    fig.update_traces(marker=dict(size=12, opacity=0.6))

    fig.update_layout(
        yaxis=dict(
            title="Stop ID",
            tickvals=result_nonan["stopid"].unique(),
            ticktext=helpers.STOP_SEQUENCES[selected_intersection][selected_route][
                selected_direction
            ],
        ),
        height=600,
        width=800,
    )

    st.plotly_chart(fig)

else:
    st.warning("No data available for the selected filters.")


complete_corridors = helpers.get_corridor_data(
    avl_data_filtered,
)


corridor_aggregated = helpers.aggregate_data_by_corridor(complete_corridors)

if not complete_corridors.empty:

    hover_columns = [
        "runtime",
        "tripdate",
        "tripid",
        "dir",
        "corridor",
        "runtime",
    ]

    fig = px.scatter(
        complete_corridors,
        x="runtime",
        y="evaluation_period",
        hover_data=hover_columns,
        color="evaluation_period",
        color_discrete_map={"before": "blue", "after": "red"},
    )

    fig.update_traces(marker=dict(size=12, opacity=0.6))

    fig.update_layout(
        xaxis=dict(tickformat=".0f"),
        template="plotly_dark",
        title=f"Corridor Runtimes for route {selected_route} ({selected_direction}) for {selected_intersection}, {selected_tod}",
        xaxis_title="runtime",
        yaxis_title="evaluation_period",
    )

    st.plotly_chart(fig)

if not corridor_aggregated.empty:

    chart = create_runtime_chart(corridor_aggregated)
    st.plotly_chart(chart, use_container_width=True)

else:
    st.warning("No data available for the selected filters.")
