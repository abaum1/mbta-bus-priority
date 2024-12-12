import pandas as pd
import numpy as np

# NOTE: this is reverse of GTFS but consistent with AVL data and excel reference provided
DIRECTION_MAPPING = {
    "in": 0,
    "out": 1,
}

INTERSECTIONS_ROUTES = {
    "Broadway": [89, 101],
    "Belmont_Mt. Auburn": [71, 73],
}

STOP_SEQUENCES = {
    "Broadway": {
        89: {
            "in": ["2703", "2705", "2709"],
            "out": ["2722", "2725", "2729"],
        },
        101: {
            "in": ["5303", "2705", "2709"],
            "out": ["2722", "2725", "2729"],
        },
    },
    "Belmont_Mt. Auburn": {
        71: {
            "in": ["2062", "2066", "2068", "2076"],
            "out": ["2076", "2026", "2028", "2032"],
        },
        73: {
            "in": ["2117", "2066", "2068", "2076"],
            "out": ["2076", "2026", "2028", "2118"],
        },
    },
}

CORRIDORS = {
    # Broadway
    "2703-2709": "89_inbound",
    "5303-2709": "101_inbound",
    "2722-2729": "101_89_outbound",
    # Mt. Auburn
    "2117-2076": "73_inbound",
    "2062-2076": "71_inbound",
    "2076-2118": "73_outbound",
    "2076-2032": "71_outbound",
}


def calculate_cv(headways):
    """
    Calculate the coefficient of variation (CV) of headways for a given stopid over a time period.
    """

    # filtered_stop_records = filtered_stop_records.sort_values("actstoptime")
    mean_headway = headways.mean()
    std_headway = headways.std()
    cv = std_headway / mean_headway if mean_headway > 0 else float("nan")

    return cv


def filter_data_by_tod_route_direction(
    avl_data, selected_route, selected_direction, selected_tod
):
    filtered_raw_avl = avl_data[
        (avl_data["dir"] == DIRECTION_MAPPING[selected_direction])
        & (avl_data["route"] == selected_route)
        & (avl_data["tod"] == selected_tod)
    ]

    return filtered_raw_avl


def compute_headway(avl_stop_observations):
    avl_stop_observations.sort_values(by=["stopid", "actstoptime"], inplace=True)


def get_corridor_data(
    intersection_raw_avl,
):

    intersection_raw_avl["actstoptime"] = pd.to_datetime(
        intersection_raw_avl["actstoptime"]
    )
    intersection_raw_avl["tripid"] = intersection_raw_avl["trip"].astype(str)

    by_trip = (
        intersection_raw_avl.groupby(
            [
                "tripid",
                "tripdate",
                "year",
                "seasonal_period",
                "dir",
                "evaluation_period",
            ]
        )
        .agg(
            start_time=("actstoptime", "min"),
            end_time=("actstoptime", "max"),
            stopid_sequence=("stopid", lambda x: ",".join(map(str, pd.unique(x)))),
            first_stop_id=(
                "actstoptime",
                lambda x: intersection_raw_avl.loc[x.idxmin(), "stopid"],
            ),
            last_stop_id=(
                "actstoptime",
                lambda x: intersection_raw_avl.loc[x.idxmax(), "stopid"],
            ),
        )
        .reset_index()
    )

    by_trip["runtime"] = (
        pd.to_datetime(by_trip["end_time"]) - pd.to_datetime(by_trip["start_time"])
    ).dt.total_seconds()
    by_trip["stopid_sequence"] = (
        by_trip["first_stop_id"].astype(str) + "-" + by_trip["last_stop_id"].astype(str)
    )

    by_trip["corridor"] = by_trip["stopid_sequence"].map(CORRIDORS)

    by_trip_filtered = by_trip[by_trip["corridor"].notnull()]

    return by_trip_filtered


def calculate_time_diff(avl_stop_observations):
    avl_stop_observations["actstoptime"] = pd.to_datetime(
        avl_stop_observations["actstoptime"]
    )
    avl_stop_observations = avl_stop_observations.sort_values(
        by=["trip", "actstoptime"]
    ).reset_index(drop=True)
    avl_stop_observations["runtime"] = (
        avl_stop_observations.groupby("trip")["actstoptime"].diff().dt.total_seconds()
    )
    avl_stop_observations["runtime"] = avl_stop_observations.apply(
        lambda row: (
            row["runtime"]
            if row.name > 0
            and row["stopid"] != avl_stop_observations.loc[row.name - 1, "stopid"]
            else None
        ),
        axis=1,
    )
    # Reset time_diff to NaN for the first row of each trip
    avl_stop_observations.loc[
        avl_stop_observations.groupby("trip").head(1).index, "runtime"
    ] = None
    avl_stop_observations = avl_stop_observations.sort_values(
        by=["trip", "actstoptime"]
    ).reset_index(drop=True)
    return avl_stop_observations


def aggregate_data_by_corridor(stop_data_filtered):

    print("COLUMNS", stop_data_filtered.columns)

    by_corridor = (
        stop_data_filtered.groupby(["evaluation_period", "dir"])
        .agg(
            median_runtime=("runtime", "median"),
            mean_runtime=("runtime", "mean"),
            num_records=("runtime", "count"),
            best_case_runtime=(
                "runtime",
                lambda x: (
                    np.percentile(x.dropna(), 5) if len(x.dropna()) > 0 else np.nan
                ),
            ),
            worst_case_runtime=(
                "runtime",
                lambda x: (
                    np.percentile(x.dropna(), 95) if len(x.dropna()) > 0 else np.nan
                ),
            ),
            # stopid_sequence=("stopid", lambda x: ",".join(map(str, pd.unique(x)))),
        )
        .reset_index()
    )

    return by_corridor


def classify_headways(df, actual_col, scheduled_col):
    """
    Classifies headways as bunched, on-time, or gapped.

    Parameters:
        df (pd.DataFrame): DataFrame containing actual and scheduled headways.
        actual_col (str): Column name for actual headways.
        scheduled_col (str): Column name for scheduled headways.

    Returns:
        pd.DataFrame: The original DataFrame with a new column `status` added.
    """

    def classify_row(row):
        if row[actual_col] < 0.5 * row[scheduled_col]:
            return "bunched"
        elif row[actual_col] > 1.5 * row[scheduled_col]:
            return "gapped"
        else:
            return "on-time"

    df["status"] = df.apply(classify_row, axis=1)
    return df


# Example usage:
# df = pd.DataFrame({'actual_headway': [...], 'scheduled_headway': [...]})
# df = classify_headways(df, actual_col='actual_headway', scheduled_col='scheduled_headway')
