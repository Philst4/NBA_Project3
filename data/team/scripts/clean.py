# IMPORTS
import pandas as pd

# Script to clean raw data, save cleaned data separately. Specifically:
# * Make 'GAME_ID' the index (with a bit of mapping)
# * Fix NaN's in PLUS_MINUS by subtracting points scored
# * FIX other NaN's by taking average for team in a given season
# * add 'IS_HOME' feature


# HELPERS 

# basic unique mapping from original index to mirror index
# * home team perspective is even
# * away team perspective is odd
def new_index_map(game_id, is_home):
    if is_home:
        return game_id * 2
    else:
        return game_id * 2 + 1

# Makes an index for the new_index using 'GAME_ID' of the raw data
def make_new_index(df_raw : pd.DataFrame) -> pd.Index:
    index = df_raw.index
    home_index = new_index_map(index, True)
    away_index = new_index_map(index, False)
    new_index = home_index.union(away_index).sort_values()
    new_index = new_index.unique() # remove duplicates
    return new_index


def make_clean_df(df_raw : pd.DataFrame) -> pd.DataFrame:
    # Use 'GAME_ID' to make new index (useful for later)
    # * new id is called 'ID'
    # * 'GAME_ID' preserved as a feature
    df_raw['ID'] = df_raw['GAME_ID'].copy()
    df_raw.set_index('ID', inplace=True)
    df_raw.sort_index(inplace=True)

    # Get new_index, initialize df_clean
    new_index = make_new_index(df_raw)
    df_clean = pd.DataFrame(index=new_index, columns=df_raw.columns)
    # Fill in df_clean

    # Share the same id's
    home_df = df_raw[df_raw['IS_HOME'] == 1]
    away_df = df_raw[df_raw['IS_HOME'] == 0]


    for i, id in enumerate(df_raw.index):
            if i % 1000 == 0: 
                print("{}/{} games added...".format(i, len(df_raw.index)))
            
            # get home and away team new id
            home_team_new_id = new_index_map(id, True)
            away_team_new_id = new_index_map(id, False)
            
            # add to df_clean
            df_clean.loc[home_team_new_id] = home_df.loc[id]
            df_clean.loc[away_team_new_id] = away_df.loc[id]

    return df_clean

def clean_plus_minus(df_clean : pd.DataFrame) -> pd.DataFrame:
    for id in df_clean.index:
        game = df_clean.loc[id]
        if pd.isna(game['PLUS_MINUS']):
            if game['IS_HOME']:
                counterpart = df_clean.loc[id + 1] # corresponding away game
            else:
                counterpart = df_clean.loc[id - 1] # corresponding home game
            
            df_clean.at[id, 'PLUS_MINUS'] = game['PTS'] - counterpart['PTS']
    
    return df_clean

def clean_other_numeric(df_clean : pd.DataFrame) -> pd.DataFrame:
    # FIX other NaN's by taking average for team in a given season
    # Group by team and season
    groups = df_clean.groupby(['TEAM_ID', 'SEASON_ID'])
    for group_key, group_df in groups:
        # Fill NaN's with mean of numeric columns
        numeric_columns = group_df.select_dtypes(include='number').columns
        group_df[numeric_columns] = group_df[numeric_columns].fillna(group_df[numeric_columns].mean())
        df_clean.loc[group_df.index] = group_df
    return df_clean


# MAIN

# Read in data

df_raw = pd.read_csv("raw/raw.csv")
df_normalized = pd.read_csv("raw/normalized.csv")
df_standardized = pd.read_csv("raw/standardized.csv")

# add 'IS_HOME' feature (useful for making new index)
df_raw['IS_HOME'] = df_raw['MATCHUP'].str.contains('vs.').astype(int)
df_normalized['IS_HOME'] = df_normalized['MATCHUP'].str.contains('vs.').astype(int)
df_standardized['IS_HOME'] = df_standardized['MATCHUP'].str.contains('vs.').astype(int)

# Make df_clean (df to-be-cleaned below)
# * Uses 'GAME_ID' and 'IS_HOME' to make new index
print(" ... Making dataframe to be cleaned ... ")
df_clean_unscaled = make_clean_df(df_raw)
df_clean_normalized = make_clean_df(df_normalized)
df_clean_standardized = make_clean_df(df_standardized)

# Fix NaN's in PLUS_MINUS by subtracting points scored
print(" ... Cleaning PLUS_MINUS ... ")
df_clean_unscaled = clean_plus_minus(df_clean_unscaled)
df_clean_normalized = clean_plus_minus(df_clean_normalized)
df_clean_standardized = clean_plus_minus(df_clean_standardized)

# FIX other NaN's by taking average for team in a given season
print(" ... Cleaning other numeric columns ... ")
df_clean_unscaled = clean_other_numeric(df_clean_unscaled)
df_clean_normalized = clean_other_numeric(df_clean_normalized)
df_clean_standardized = clean_other_numeric(df_clean_standardized)

print(" ... Making 'WL' numeric ... ")
df_clean_unscaled['WL'] = df_clean_unscaled['WL'].map({'W': 1, 'L': 0})
df_clean_normalized['WL'] = df_clean_normalized['WL'].map({'W': 1, 'L': 0})
df_clean_standardized['WL'] = df_clean_standardized['WL'].map({'W': 1, 'L': 0})



# Save unscaled and scaled to csv
# NOTE: want to keep ID's (useful for later)
print("... Saving all ... ")
df_clean_unscaled.to_csv("cleaned/unscaled.csv", index=True)

df_clean_normalized.to_csv("cleaned/normalized.csv", index=True)

df_clean_standardized.to_csv("cleaned/standardized.csv", index=True)
    
    