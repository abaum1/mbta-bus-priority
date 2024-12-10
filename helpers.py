import pandas as pd
import numpy as np


DIRECTION_MAPPING = {
    "in": 1,
    "out": 0,
}

INTERSECTIONS_ROUTES = {
    "Broadway": [89, 101],
    "mtauburn": [71, 73],
    "s_mass_ave": [1],
}

CORRIDORS = {
    # Broadway
    "2703,2705,2709": "89_inbound",
    "5303,2705,2709": "101_inbound",
    "2722,2725,2729": "101_89_outbound",
    # Mt. Auburn
    "2117,2066,2068,2076": "73_inbound",
    "2062,2066,2068,2076": "71_inbound",
    "2076,2026,2028,2118": "73_outbound",
    "2076,2026,2028,2032": "71_outbound",
}


def assign_period(row):
    if row["year"] < 2019:
        return "before"
    elif row["year"] == 2019:
        if row["seasonal_period"] < 2:
            return "before"
        elif row["seasonal_period"] == 2:
            return "after"
    else:
        return "after"


def get_corridor_data(intersection_raw_avl, selected_direction, selected_route):

    filtered_raw_avl = intersection_raw_avl[
        (intersection_raw_avl["dir"] == DIRECTION_MAPPING[selected_direction])
        & (intersection_raw_avl["route"] == selected_route)
    ]
    filtered_raw_avl["actstoptime"] = pd.to_datetime(filtered_raw_avl["actstoptime"])
    filtered_raw_avl["tripid"] = filtered_raw_avl["trip"].astype(str)

    filtered_trips = filtered_raw_avl.groupby(
        ["tripid", "tripdate", "year", "seasonal_period", "dir"]
    ).filter(lambda group: group["stopid"].nunique() == 3)

    by_trip = (
        filtered_trips.groupby(["tripid", "tripdate", "year", "seasonal_period", "dir"])
        .agg(
            start_time=("actstoptime", "min"),
            end_time=("actstoptime", "max"),
            stopid_sequence=("stopid", lambda x: ",".join(map(str, pd.unique(x)))),
        )
        .reset_index()
    )

    by_trip["runtime"] = (
        pd.to_datetime(by_trip["end_time"]) - pd.to_datetime(by_trip["start_time"])
    ).dt.total_seconds()
    by_trip["period"] = by_trip.apply(assign_period, axis=1)
    by_trip["corridor"] = by_trip["stopid_sequence"].map(CORRIDORS)

    return by_trip


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

    print(stop_data_filtered["runtime"].head())
    by_corridor = (
        stop_data_filtered.groupby(["period", "dir"])
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
            # stopid_sequence=("stopid", lambda x: ",".join(map(str, pd.unique(x)))),
        )
        .reset_index()
    )

    return by_corridor
