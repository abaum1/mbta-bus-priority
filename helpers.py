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
    return intersection_raw_avl
