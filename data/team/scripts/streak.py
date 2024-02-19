import pandas as pd
import time


# HELPERS

# Makes the column names for <streak_df> using mirror_df's columns
# * Stat columns are renamed to include '_prev_k' for each k in <ks>
def make_streak_col(col, k):
    return "{}_prev_{}".format(col, k)


# Makes df where all data instances have perspective from both teams
# As team for, and as team against
def make_AB(df : pd.DataFrame) -> pd.DataFrame:
    # Initialize df from team A's perspective
    df_A = df.copy()

    # rename columns to reflect team A's perspective
    for col in df_A.columns:
        df_A.rename(columns={col: col + '_A'}, inplace=True)

    # Initialize df from team B's perspective
    df_B = pd.DataFrame(index=df.index, columns = df.columns)

    # Switch even and odd entries
    for i in df.index:
        if i % 2 == 0:  # If index is even
            df_B.loc[i] = df.loc[i + 1]  # Swap with the next row
        else:
            df_B.loc[i] = df.loc[i - 1]  # Swap with the previous row
    
    # rename columns to reflect team B's perspective
    for col in df_B.columns:
        df_B.rename(columns={col: col + '_B'}, inplace=True)

    # merge the two dataframes by game_id
    df_AB = pd.merge(df_A, df_B, left_index=True, right_index=True)

    return df_AB



# Main function. 
# Makes <streak_df> with same index as <mirror_df>, columns tracking stats over previous 'k' games, leading up to the corresponding game in <df>
# over prev 'k' games leading up to the corresponding game in <mirror_df>
# * Streaks only made using games from the same season
# * k = 0 -> streaks made using all previous games
def make_streak_df(mirror_df : pd.DataFrame, ks: list, non_streak_features : list) -> pd.DataFrame:

    # Make winloss into numeric
    mirror_df['WL_for'] = mirror_df['WL_for'].map({'W': 1, 'L': 0})
    mirror_df['WL_against'] = mirror_df['WL_against'].map({'W': 1, 'L': 0})
    
    # Columns to leave out of streaks
    leave_out_cols = non_streak_features

    # Select columns to streak
    are_streak_cols = ~mirror_df.columns.isin(leave_out_cols)
    cols_to_streak = list(mirror_df.columns[are_streak_cols])

    streak_cols = []
    for k in ks:
        for col in cols_to_streak:
            streak_col = make_streak_col(col, k)
            streak_cols.append(streak_col)

    # Initializes empty <streak_df>, same index as <mirror_df>
    index = mirror_df.index
    more_cols = ['k_length'] # should be useful
    #new_cols = leave_out_cols + cols_to_streak + streak_cols + more_cols
    new_cols = streak_cols + more_cols
    
    
    streak_df = pd.DataFrame(index=index, columns=new_cols)

        # Adds data to <streak_df> using streaks from the same season
    print("k values: {}".format(ks))
    print("features: {}".format(new_cols))
    
    
    # Sort <streak_df> by season
    #mirror_df = mirror_df.sort_values(by='SEASON_ID')
    seasons = mirror_df['SEASON_ID'].unique()
    
    
    for i, season in enumerate(seasons):
        print("Season {}/{}".format(i+1, len(seasons)))
        
        season_start_time = time.time()
        
        
        # Make a df for the current season, sort by team
        season_df = mirror_df[mirror_df['SEASON_ID'] == season]
        season_df.sort_values(by='TEAM_ID_for')
        
        teams = season_df['TEAM_ID_for'].unique()
        
        for j, team in enumerate(teams):
            print("Team {}/{}".format(j+1, len(teams)))
            
            # Make a df for the current team, sort by date
            team_df = season_df[season_df['TEAM_ID_for'] == team]
            team_df = team_df.sort_values(by='GAME_DATE')
            
            for id in team_df.index:
                game_date = team_df.loc[id, 'GAME_DATE']
                prev_games = team_df[team_df['GAME_DATE'] < game_date]
                prev_games = prev_games.sort_values(by='GAME_DATE', ascending=False)
                
                # add stat col data to <streak_df>
                for k in ks:
                    if k == 0:
                        # Contains stats calculated from all previous games
                        prev_k_games = prev_games
                    else:
                        prev_k_games = prev_games.head(k)
                    
                    k_length = prev_k_games.shape[0]
                    streak_df.at[id, 'k_length'] = k_length
                    
                    for col in cols_to_streak:
                        streak_col = make_streak_col(col, k)
                        streak_df.at[id, streak_col] = prev_k_games[col].mean()

                    
                
                
                """# add leave_out_col data to <streak_df> 
                # May revisit later to make this more efficient
                for col in cols_to_streak + leave_out_cols:
                    streak_df.at[id, col] = team_df.at[id, col]"""

        season_end_time = time.time()
        print("Season time: ", season_end_time - season_start_time, "seconds")
        
    return streak_df


# FUNCTIONALITY FOR DEALING WITH (ALREADY CREATED) STREAK_DF
        
# Features that have nonstreak counterparts
def get_streak_features(streak_df : pd.DataFrame) -> list:
    streak_cols = [col for col in streak_df.columns if '_prev_' in col]
    return streak_cols

def get_corresponding_non_streak_features(streak_cols, k=0):
    if type(streak_cols) != list:
        streak_cols = [streak_cols]
    
    non_streak_cols = [streak_col.replace('_prev_{}'.format(k), '') for streak_col in streak_cols]
    return non_streak_cols


# Main function 

if __name__ == "__main__":

    # Makes <streak_df> of streak data with, same index as <mirror_df>,
    # columns tracking stats over previous 'k' games, leading up to 
    # the corresponding game in <df>

    start = time.time()

    # Read in mirror_df
    mirror_df_standardized = pd.read_csv('mirrored/standardized.csv', index_col=0)

    # Set k-values
    ks = [0]

    # Specify which columns NOT to streak
    leave_out_cols = ['SEASON_ID', 'GAME_DATE', 
            'TEAM_ABBREVIATION_for', 'TEAM_ABBREVIATION_against',
            'TEAM_NAME_for', 'TEAM_NAME_against',
            'MATCHUP_for', 'MATCHUP_against']

    # Make streak_df
    streak_df_standardized = make_streak_df(mirror_df_standardized, ks, leave_out_cols)

    
    streak_df_standardized.to_csv('streaked/standardized_0.csv', index=True)

    end = time.time()

    print(end - start, "seconds total")