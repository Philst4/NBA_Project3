import pandas as pd
import time


# HELPERS

# Function that makes the mirror_df
def make_mirror_df(clean_df : pd.DataFrame) -> pd.DataFrame:
    
    # Make columns for mirror_df
    cols_for = [col + "_for" for col in clean_df.columns]
    cols_against = [col + "_against" for col in clean_df.columns]
    mirror_cols = cols_for + cols_against

    # Make mirror_df; where to put new data
    mirror_df = pd.DataFrame(index=clean_df.index, columns=mirror_cols) 


    # group games by game_id
    groups_df = clean_df.groupby('GAME_ID') 

    i = 0 # for inserting into mirror_df

    for group_key, group_df in groups_df:
        # Select both game instances
        game_instance_1 = group_df.iloc[0]
        game_instance_2 = group_df.iloc[1]
        
        # Make mirror instances
        game_instance_mirror1 = {}
        game_instance_mirror2 = {}
        for col in game_instance_1.index:
            
            # First perspective
            game_instance_mirror1[col + "_for"] = game_instance_1[col]
            game_instance_mirror1[col + "_against"] = game_instance_2[col]
            
            # Second perspective
            game_instance_mirror2[col + "_for"] = game_instance_2[col]
            game_instance_mirror2[col + "_against"] = game_instance_1[col]
        
        # Add to mirror_df
        mirror_df.iloc[i] = game_instance_mirror1
        mirror_df.iloc[i + 1] = game_instance_mirror2
        
        i += 2

    # consolidate redundant columns (e.g. GAME_ID_for and GAME_ID_against => GAME_ID)
    # Makes more sense to leave out of initial mirroring. To revisit
    redundant_cols = ['GAME_ID', 'GAME_DATE', 'SEASON_ID']
    
    for feature in redundant_cols:
        mirror_df[feature] = mirror_df[feature + "_for"]
        mirror_df.drop(columns=[feature + "_for", feature + "_against"], inplace=True)
    

    return mirror_df



# MAIN

clean_df_unscaled = pd.read_csv("cleaned/unscaled.csv", index_col=0)
clean_df_normalized = pd.read_csv("cleaned/normalized.csv", index_col=0)
clean_df_standardized = pd.read_csv("cleaned/standardized.csv", index_col=0)


start = time.time()
print(" ... Making mirror_df unscaled...")
mirror_df_unscaled = make_mirror_df(clean_df_unscaled)

print(" ... Making mirror_df standardized ...")
mirror_df_standardized = make_mirror_df(clean_df_standardized)

print(" ... Making mirror_df normalized ...")
mirror_df_normalized = make_mirror_df(clean_df_normalized)

end = time.time()
print("Time: ", end - start)

# Save files
mirror_df_unscaled.to_csv("mirrored/unscaled.csv", index=True)
mirror_df_normalized.to_csv("mirrored/normalized.csv", index=True)
mirror_df_standardized.to_csv("mirrored/standardized.csv", index=True)
