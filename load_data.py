import os
import sqlite3
import pandas as pd

##############################
### Part 1: Data Management
##############################
# Relational database schema can be visualized at images/ER-Diagram.png.

# read in cell count data
print("Reading in cell count file data...")
project_df = pd.read_csv("cell-count.csv", header=0)

if os.path.exists("drug-response.db"):
    os.remove("drug-response.db")

# create connection to DB
print("Creating connection to drug-response.db...")
try:
    with sqlite3.connect("drug-response.db") as con:

        # database cursor for querying and executing SQL
        cur = con.cursor()

        cur.execute("PRAGMA foreign_keys = ON")

        # initialize tables for DB
        print("Initializing tables in database...")
        cur.execute("""CREATE TABLE IF NOT EXISTS project_info(
                        project_id  TEXT PRIMARY KEY
                        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS patients(
                        patient_id   TEXT PRIMARY KEY,
                        sex          TEXT,
                        age          INTEGER,
                        condition    TEXT,
                        treatment    TEXT,
                        response     INTEGER,
                        project_id   TEXT,
                        FOREIGN KEY(project_id) REFERENCES project_info(project_id)
                        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS samples(
                        sample_id                   TEXT PRIMARY KEY,
                        sample_type                 TEXT,
                        time_from_treatment_start   INTEGER,
                        patient_id                  TEXT,
                        FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
                        )
                    """)

        cur.execute("""CREATE TABLE IF NOT EXISTS cell_counts(
                        sample_id   TEXT,
                        cell_type   TEXT,
                        count       INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY(sample_id, cell_type),
                        FOREIGN KEY(sample_id) REFERENCES samples(sample_id)
                        )
                    """)

        # rename and transform data for SQLite tables
        print("Processing dataset to meet table requirements...")
        project_df = project_df.rename(columns={'project': 'project_id', 
                                                'subject': 'patient_id',
                                                'sample': 'sample_id'})
        project_df['response'] = project_df['response'].replace({'yes':1, 'no':0})
        
        # change cell counts data from wide to long format
        counts_df = project_df.loc[:,['sample_id', 'b_cell', 'cd8_t_cell', 
                                    'cd4_t_cell', 'nk_cell', 'monocyte']]
        counts_df = counts_df.melt(id_vars='sample_id', 
                                value_vars=['b_cell', 'cd8_t_cell', 
                                            'cd4_t_cell', 'nk_cell', 
                                            'monocyte'],
                                var_name='cell_type',
                                value_name='count')


        # insert all info from original df into the respective tables
        print("Inserting rows into tables...")
        project_df[['project_id']].drop_duplicates().to_sql(
                                                    name='project_info', 
                                                    con=con, 
                                                    if_exists='append', 
                                                    index=False)

        project_df.drop_duplicates(subset='patient_id').loc[:,
            ['patient_id', 'sex', 'age', 'condition', 'treatment',
             'response', 'project_id']].to_sql(name='patients', 
                                            con=con, 
                                            if_exists='append', 
                                            index=False)

        project_df.drop_duplicates(subset='sample_id').loc[:,
            ['sample_id', 'sample_type', 'time_from_treatment_start', 
             'patient_id']].to_sql(name='samples', 
                                con=con, 
                                if_exists='append', 
                                index=False)

        counts_df.loc[:,['sample_id', 'cell_type', 'count']].to_sql(
                                                        name='cell_counts', 
                                                        con=con, 
                                                        if_exists='append', 
                                                        index=False)
except sqlite3.Error as e:
    print("Database connection failed with: \n", e)

print("Success loading in data! Changes committed to database.\n")

