import pandas as pd
import helpers


broadway_allroutes_data = []
for route in ["89", "101"]:
    for direction in ["in", "out"]:
        intersection_raw_avl = pd.read_csv(
            f"data/AVL_2019/Broadway/R{route}_{direction}.csv"
        )
        broadway_allroutes_data.append(intersection_raw_avl)
broadway_df = pd.concat(broadway_allroutes_data)

broadway_df_processed = helpers.calculate_time_diff(broadway_df)
broadway_df_processed.to_csv("processed_data/Broadway.csv", index=False)

mtauburn_allroutes_data = []
for route in ["71", "73"]:
    for direction in ["in", "out"]:
        intersection_raw_avl = pd.read_csv(
            f"data/AVL_2019/Belmont_Mt. Auburn/R{route}_{direction}.csv"
        )
        mtauburn_allroutes_data.append(intersection_raw_avl)
mtauburn_df = pd.concat(mtauburn_allroutes_data)

mtauburn_df_processed = helpers.calculate_time_diff(mtauburn_df)
mtauburn_df_processed.to_csv("processed_data/Belmont_Mt. Auburn.csv", index=False)
