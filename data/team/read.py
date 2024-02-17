import pandas as pd
import numpy as np

from nba_api.stats.endpoints import leaguegamefinder


# HELPERS

def season_to_str(season : int) -> str:
    return str(season) + '-' + str(season + 1)[-2:]


# ------- MAIN -------- 
# PURPOSE IS TO READ IN ALL REGULAR SEASON GAMES
# WITH RELEVANT DATA



path = "data/raw/raw.csv"

print("File not found, creating new DataFrame")
raw_df = pd.DataFrame()


# Seasons to query from
seasons = np.arange(1983, 2024)



# Query the API for games played in the 2023-24 season
for season in seasons: # to change range
    print("Season: ", season)

    try:
        gamefinder = leaguegamefinder.LeagueGameFinder(
            season_nullable=season_to_str(season), # specify the season
            season_type_nullable="Regular Season", # specify the season type
            league_id_nullable='00') # specify the league (NBA)
        

        # The first DataFrame of those returned is what we want.
        season_df = gamefinder.get_data_frames()[0]

        print("Number of games: {}".format(season_df.shape[0])) # Number of games played

        if raw_df.index is None:
            raw_df.index = season_df.index
        
        raw_df = pd.concat([raw_df, season_df], ignore_index=True)
    
    except Exception as e:
        print("Error: ", e)
        
raw_df.to_csv(path, index=False)
        
    