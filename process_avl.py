import pandas as pd
import helpers
from datetime import time


def assign_tod_period(row):
    dt = pd.to_datetime(row["actstoptime"])
    if time(7, 30) <= dt.time() <= time(9, 30):
        return "AM Peak"
    elif time(12, 00) <= dt.time() <= time(14, 00):
        return "Midday"
    if time(16, 30) <= dt.time() <= time(18, 30):
        return "PM Peak"


def compute_stop_headway(group):
    group = group.sort_values("actstoptime", ascending=True)
    group["headway"] = group["actstoptime"].diff().dt.total_seconds()

    return group


def assign_evaluation_period(row, intersection):

    if intersection == "Broadway":
        if row["tripdate"] < "2019-11-01":
            return "before"
        else:
            return "after"

    elif intersection == "Belmont_Mt. Auburn":
        if row["tripdate"] < "2018-11-01":
            return "before"
        else:
            return "after"
    else:
        return None


def process_intersection_avl(intersection_name, routes):
    allroutes_data = []
    for route in routes:
        for direction in ["in", "out"]:
            intersection_raw_avl = pd.read_csv(
                f"data/AVL_2019/{intersection_name}/R{route}_{direction}.csv"
            )
            allroutes_data.append(intersection_raw_avl)
    df = pd.concat(allroutes_data)

    df_processed = helpers.calculate_time_diff(df)

    df_processed["evaluation_period"] = df_processed.apply(
        lambda row: assign_evaluation_period(row, intersection_name), axis=1
    )
    df_processed["tod"] = df_processed.apply(lambda row: assign_tod_period(row), axis=1)

    with_headways = (
        df_processed.groupby(["stopid", "tripdate"])
        .apply(compute_stop_headway)
        .reset_index(drop=True)
    )

    with_headways.to_csv(f"processed_data/{intersection_name}.csv", index=False)


process_intersection_avl("Belmont_Mt. Auburn", ["71", "73"])
process_intersection_avl("Broadway", ["89", "101"])
