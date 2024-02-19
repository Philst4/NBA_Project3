import pandas as pd
from streak import get_streak_features, get_corresponding_non_streak_features

# FUNCTIONS

# This function is for adding stats pertaining to home advantage 
# over a streak to the streak_df. 
# Remember, 'IS_HOME_for_prev_k_A' is the fraction of home games 
# played over the recorded streak, and we can use this to calculate 
# the actual number of home and away games played over the streak 
# as such: 
# * NUM_HOME_for_prev_0_A = ('IS_HOME_for_prev_0_A' x 'k_length_A')
# * NUM_AWAY_for_prev_0_A = ('k_length_A' - 'NUM_HOME_for_prev_0_A')
#
# Finally, we can use these calculated values to calculate the 
# home advantage over the streak as such:
# * HOME_ADVANTAGE_for_prev_0_A = 'NUM_HOME_for_prev_0_A' - 'NUM_AWAY_for_prev_0_A')
def make_home_adv_stats(streak_df : pd.DataFrame) -> pd.DataFrame:
    home_advantage_df = pd.DataFrame(index=streak_df.index)
    home_advantage_df['NUM_HOME_for_prev_0'] = streak_df['IS_HOME_for_prev_0'] * streak_df['k_length']
    home_advantage_df['NUM_AWAY_for_prev_0'] = streak_df['k_length'] - home_advantage_df['NUM_HOME_for_prev_0']
    home_advantage_df['HOME_ADVANTAGE_for_prev_0'] = home_advantage_df['NUM_HOME_for_prev_0'] - home_advantage_df['NUM_AWAY_for_prev_0']
    
    home_advantage_df['NUM_HOME_for_prev_0_opp'] = streak_df['IS_HOME_for_prev_0_opp'] * streak_df['k_length_opp']
    home_advantage_df['NUM_AWAY_for_prev_0_opp'] = streak_df['k_length_opp'] - home_advantage_df['NUM_HOME_for_prev_0_opp']
    home_advantage_df['HOME_ADVANTAGE_for_prev_0_opp'] = home_advantage_df['NUM_HOME_for_prev_0_opp'] - home_advantage_df['NUM_AWAY_for_prev_0_opp']
    
    # Fill na's with 0
    home_advantage_df.fillna(0, inplace=True)
    
    return home_advantage_df


# This function is for flattening the streak stats wrt home advantage, 
# i.e. taking the home advantage over the previous streak out of the
# streak_df and into the main df. For instance, if a team has played 
# one more home game than an away game over its previous k games, then
# its streak stats will be inflated by 1 * the mean of the home advantage
# for each stat. 
# NOTE: 
# This function is trying to find stats in an imaginary 'neutral' site.
# In reality, this site doesn't exist; stats from home games are inflated,
# and stats from away games are deflated. 
def remove_prev_home_inflation(df : pd.DataFrame, streak_df : pd.DataFrame) -> pd.DataFrame:
    
    # make df containing home advantage stats
    print(" ... Calculating previous home advantages ... ")
    home_adv_prev = make_home_adv_stats(streak_df)
    
    print(" ... Calculating home inflation ... ")
    # Find mean advantage each stat incurs for being home
    home_inflation = ((df[df['IS_HOME_for'] == 1]).mean() - df.mean())
    # set NaN's to 0
    home_inflation.fillna(0, inplace=True)

    """print(home_inflation[[
        'FG_PCT_for', 'FG_PCT_against', 'FG_PCT_for_opp', 'FG_PCT_against_opp']])"""
        
    """print(home_adv_df[[
        'NUM_HOME_for_prev_0', 'NUM_AWAY_for_prev_0', 
        'NUM_HOME_for_prev_0_opp', 'NUM_AWAY_for_prev_0_opp',
        'HOME_ADVANTAGE_for_prev_0', 'HOME_ADVANTAGE_for_prev_0_opp']].iloc[1000])
    input()"""
    
    
    # Remove inflation
    print(" ... Deflating stats ... ")
    streak_cols = get_streak_features(streak_df)
    for streak_col in streak_cols:
        col = get_corresponding_non_streak_features(streak_col, k=0)[0]
        if 'opp' not in streak_col:
            k = streak_df['k_length']
            home_adv = home_adv_prev['HOME_ADVANTAGE_for_prev_0']
            
            # take out home inflation from streak stats
            streak_df[streak_col] -= (home_adv * home_inflation[col]) / k 
        else:
            k = streak_df['k_length_opp']
            home_adv = home_adv_prev['HOME_ADVANTAGE_for_prev_0_opp']
            
            # take out home inflation
            streak_df[streak_col] -= (home_adv * home_inflation[col]) / k
    
    return streak_df


# factor in whether or not the current game is a home game
# meant to be used after remove_prev_home_inflation
def add_curr_home_inflation(streak_df : pd.DataFrame, df : pd.DataFrame):
    
    home_inflation = ((df[df['IS_HOME_for'] == 1]).mean() - df.mean())
    # set NaN's to 0
    home_inflation.fillna(0, inplace=True)
    
    
    
    home_adv_curr = df['IS_HOME_for'].map({0: -1, 1: 1})
    
    streak_cols = get_streak_features(streak_df)
    for streak_col in streak_cols:
        col = get_corresponding_non_streak_features(streak_col, k=0)[0]
        if 'opp' not in streak_col:
            
            # put in current home inflation to streak stats
            streak_df[streak_col] += (home_adv_curr * home_inflation[col]) 
        else:
            
            # put in current home inflation to streak stats
            streak_df[streak_col] += (home_adv_curr * home_inflation[col])
    
    return streak_df
    




if __name__ == "__main__":

    df = pd.read_csv('opped/standardized.csv', index_col=0).select_dtypes(include='number')
    streak_df = pd.read_csv('opped/standardized_0.csv', index_col=0).select_dtypes(include='number')
    
    # Level off home inflation from streak df
    leveled_df = remove_prev_home_inflation(df, streak_df)
    
    inflated_df = add_curr_home_inflation(leveled_df, df)
    
    inflated_df.to_csv('deflated/standardized_0.csv', index=True)
    
    