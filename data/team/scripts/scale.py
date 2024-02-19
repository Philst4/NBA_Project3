# IMPORTS
import pandas as pd

# Script to scale data by season. Specifically, can either:
# * normalize data by season
# * standardize data by season



# Normalizes the data by season
def normalize_by_season(df : pd.DataFrame, cols : list) -> pd.DataFrame:
    # Make a copy of the df
    df_normalized = df.copy()
    
    # Group by season
    groups = df.groupby('SEASON_ID')
    
    # Scale each season
    for season, group in groups:
        for col in cols:
            season_min = group[col].min(skipna=True)
            season_max = group[col].max(skipna=True)
            df_normalized.loc[group.index, col] = (group[col] - season_min) / (season_max - season_min)
        
    return df_normalized



# Standardizes the data by season
def standardize_by_season(df : pd.DataFrame, cols : list) -> pd.DataFrame:
    # Make a copy of the df
    df_standardized = df.copy()
    
    # Group by season
    groups = df.groupby('SEASON_ID')
    
    # Scale each season
    for season, group in groups:
        for col in cols:
            season_mean = group[col].mean(skipna=True)
            season_std = group[col].std(skipna=True)
            df_standardized.loc[group.index, col] = (group[col] - season_mean) / season_std
        
    return df_standardized



# MAIN
# Read in data
raw_df = pd.read_csv("raw/raw.csv")

# Create version with scaled statistical columns
cols_to_scale = ['MIN', 'PTS', 
                 'FGM', 'FGA', 'FG_PCT',
                 'FG3M', 'FG3A', 'FG3_PCT', 
                 'FTM', 'FTA','FT_PCT', 
                 'OREB', 'DREB', 'REB', 
                 'AST', 'STL', 'BLK', 
                 'TOV', 'PF', 'PLUS_MINUS']



df_normalized = normalize_by_season(raw_df, cols_to_scale)
df_standardized = standardize_by_season(raw_df, cols_to_scale)

df_normalized.to_csv("raw/normalized.csv", index=False)
df_standardized.to_csv("raw/standardized.csv", index=False)