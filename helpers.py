import pandas as pd


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


def get_intersection_data(selected_intersection, selected_direction, selected_route):

    intersection_raw_avl = pd.read_csv(
        f"data/AVL_2019/{selected_intersection}/R{selected_route}_{selected_direction}.csv"
    )

    intersection_with_runtime = calculate_time_diff(intersection_raw_avl)
    intersection_with_runtime["period"] = intersection_with_runtime.apply(
        assign_period, axis=1
    )

    return intersection_with_runtime


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
