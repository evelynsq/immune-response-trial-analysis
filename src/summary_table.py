import os
import sqlite3
import pandas as pd

###############################################
### Part 2: Initial Analysis (Data Overview)
###############################################

os.makedirs('outputs/part-2', exist_ok=True)

def freq_table(db_file: str) -> pd.DataFrame:
    """
    input:
    db_file - database file containing all trial data
    
    output:
    Pandas dataframe containing relative frequencies of cell
    populations in each sample

    Creates a summary table with relative frequencies of each
    cell population per sample
    """
    counts_df = pd.DataFrame()
    try:
        with sqlite3.connect(db_file) as con:
            # read cell counts from SQLite to pandas df
            counts_df = pd.read_sql_query('SELECT * FROM cell_counts', con)
            counts_df = counts_df.rename(columns={'sample_id':'sample', 
                                                  'cell_type':'population'})
            
            # get total count & relative freqs of each population by sample
            counts_df['total_count'] = counts_df.groupby(
                    'sample')[['count']].transform('sum')
            counts_df['percentage'] = (counts_df['count'] / counts_df['total_count']) * 100
            counts_df['percentage'] = counts_df['percentage']

            # rearrange columns in correct order
            counts_df = counts_df.iloc[:,[0,3,1,2,4]]

    except sqlite3.Error as e:
        print("Database connection failed with: \n", e)

    return counts_df

if __name__ == "__main__":
    # the call to the function below will run with 'make pipeline', and
    # assumes you are in the project root directory (not inside 'outputs' subdir)
    freq_table('drug-response.db').to_csv(
        './outputs/part-2/relative-frequencies.csv', index=False)

    print("Successfully created cell population relative frequencies table!")
    print("See outputs/relative-frequencies.csv in 'outputs' subdirectory for table.\n")
