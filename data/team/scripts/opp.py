import pandas as pd

# Makes df where all data instances have perspective from both teams
# * Team making predictions for (TEAM A)
# * Opposing team (TEAM B)
# * df adds flag '_opp' to all columns of opposing team's stats
def make_opp(df : pd.DataFrame) -> pd.DataFrame:
    # Initialize df from team A's perspective
    df_A = df.copy()

    # Initialize df opponent's (team B's) perspective
    df_B = pd.DataFrame(index=df.index, columns = df.columns)

    # Switch even and odd entries
    for i in df.index:
        if i % 2 == 0:  # If index is even
            df_B.loc[i] = df.loc[i + 1]  # Swap with the next row
        else:
            df_B.loc[i] = df.loc[i - 1]  # Swap with the previous row
    
    # rename columns to reflect team B's perspective
    for col in df_B.columns:
        df_B.rename(columns={col: col + '_opp'}, inplace=True)

    # merge the two dataframes by game_id
    df_AB = pd.merge(df_A, df_B, left_index=True, right_index=True)

    return df_AB


streak_df_standardized = pd.read_csv("mirrored/standardized.csv", index_col=0)


# Make from A and B perspectives
print("... Adding opposing perspective ...")
#print(" * Unscaled")
#streak_df_AB = make_AB(streak_df)
print(" * Standardized ")
streak_df_opp_standardized = make_opp(streak_df_standardized)

streak_df_opp_standardized.to_csv('opped/standardized.csv', index=True)
