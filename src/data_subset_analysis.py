import os
import sqlite3
import pandas as pd

###################################
### Part 4: Data Subset Analysis
###################################

if not os.path.isdir('outputs/part-4'):
    os.mkdir('outputs/part-4')

def sample_counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    inputs:
    df - Pandas dataframe with samples
    col - Column of interest in df to count samples by

    output:
    Pandas dataframe with the final output format

    Find the number of samples per each unique value in a column (col),
    and put data in correct output dataframe format
    """
    # get counts of each unique value in col
    samp_num = df[col].value_counts().reset_index()

    # create new column labels
    samp_num.columns = ['label', 'num_samples']
    samp_num['category'] = col

    # also add % of total samples that one label's samples consist of
    samp_num['pct_total_samples'] = (samp_num['num_samples'] / 
                                float(samp_num['num_samples'].sum())) * 100
    samp_num['pct_total_samples'] = samp_num['pct_total_samples'].map(
                                                        '{:.3f}'.format)

    # change order of columns
    samp_num = samp_num.iloc[:,[2,0,1,3]]

    return samp_num

try:
    with sqlite3.connect('drug-response.db') as con:
        # ID all melanoma PBMC samples at baseline (t=0) from miraclib patients
        initial_query = pd.read_sql_query("""
                SELECT 
                    p.patient_id,
                    p.condition,
                    p.treatment,
                    p.response,
                    p.sex,
                    p.project_id,                    
                    s.sample_id,
                    s.sample_type,
                    s.time_from_treatment_start
                    FROM patients p
                    INNER JOIN samples s ON s.patient_id = p.patient_id
                    WHERE
                    s.sample_type = 'PBMC' AND
                    s.time_from_treatment_start = 0 AND
                    p.condition = 'melanoma' AND
                    p.treatment = 'miraclib'
                    """, con)
        initial_query['response'] = initial_query['response'].replace({1:'yes', 
                                                                       0:'no'})

        print("Successfully completed initial query, saving results to",
              "initial-query-data.csv in the 'outputs' subdirectory.")
        initial_query.to_csv('./outputs/part-4/initial-query-data.csv', 
                             index=False)

        ## Extending the query
        # how many samples are from each project
        project_df = sample_counts(initial_query, 'project_id')
        project_df.to_csv('./outputs/part-4/samples-per-project.csv', 
                          index=False)
        print("Number of filtered samples for each project written to",
              'outputs/part-4/samples-per-project.csv.')

        # how many subjects are responders/non-responders
        response_df = sample_counts(initial_query, 'response')
        response_df.to_csv('./outputs/part-4/samples-per-response.csv', 
                           index=False)
        print("Number of filtered samples for each response status written to",
              'outputs/part-4/samples-per-response.csv.')

        # how many subjects are M/F
        gender_df = sample_counts(initial_query, 'sex')
        gender_df.to_csv('./outputs/part-4/samples-per-gender.csv', 
                         index=False)
        print("Number of filtered samples for each gender written to",
              'outputs/part-4/samples-per-gender.csv.')

except sqlite3.Error as e:
    print("Database connection failed with: \n", e)


# Google form question:
# What is the avg number of B cells for Melanoma male responders at time=0? 
try:
    with sqlite3.connect('drug-response.db') as con:
        # query for melanoma males who are responders, then
        # filter to only get B cells for t=0 samples
        mel_males = pd.read_sql_query("""
            SELECT
            p.patient_id,
            p.sex,
            p.condition,
            p.response,
            s.sample_id,
            s.time_from_treatment_start,
            c.cell_type,
            c.count
            FROM patients p
            JOIN samples s ON s.patient_id = p.patient_id
            JOIN cell_counts c ON c.sample_id = s.sample_id
            WHERE 
            p.sex = 'M' AND
            p.condition = 'melanoma' AND
            p.response = 1 AND
            s.time_from_treatment_start = 0 AND
            c.cell_type = 'b_cell'
            """, con)

        # find avg number of B cells for the above samples
        b_cell_avg = float(mel_males['count'].mean())

        print(f"There is an average number of {b_cell_avg:.2f} B cells",
              "for melanoma male patients who were responders.\n")

except sqlite3.Error as e:
    print("Database connection failed with: \n", e)