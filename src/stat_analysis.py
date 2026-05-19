import os
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
from scipy import stats
import seaborn as sns
import sqlite3
import pandas as pd

###################################
### Part 3: Statistical Analysis
###################################

if not os.path.isdir('outputs/part-3'):
    os.mkdir('outputs/part-3')

def filter_table(freq_table: pd.DataFrame, db_file: str, condition: str,
                 treatment: str, sample_type: str) -> pd.DataFrame:
    """
    inputs:
    freq_table - relative freq table generated from Part 2
    db_file - DB file containing trial data
    condition - condition (i.e. disease) to filter by
    treatment - treatment (i.e. drug) to filter by
    sample_type - sample type to filter by

    outputs:
    Dataframe filtered based on metadata provided.

    Filters summary table from Part 2 based on metadata.
    """
    filtered_df = pd.DataFrame()
    try:
        with sqlite3.connect(db_file) as con:
            # read in SQLite metadata into a pandas df
            meta_df = pd.read_sql_query(
                """SELECT s.sample_id,
                    s.sample_type,
                    s.time_from_treatment_start,
                    p.patient_id,
                    p.condition,
                    p.treatment,
                    p.response
                FROM samples s
                INNER JOIN patients p ON p.patient_id = s.patient_id""",
                con)
            meta_df = meta_df.rename(columns={'sample_id': 'sample'})
            meta_df['response'] = meta_df['response'].replace({1:'yes',
                                                               0:'no'})

            # left join relative frequencies table with metadata
            freq_table = freq_table.merge(meta_df, on='sample', how='left')

            # filter frequencies data based on metadata specified in args
            if condition is not None:
                filtered_df = freq_table[(freq_table['condition'] == condition)]
                
            if treatment is not None:
                filtered_df = filtered_df[(filtered_df['treatment'] == treatment)]
            
            if sample_type is not None:
                filtered_df = filtered_df[(filtered_df['sample_type'] == sample_type)]

    except sqlite3.Error as e:
        print("Database connection failed with: \n", e)
    
    return filtered_df


def create_boxplot(csv_file: str) -> None:
    """
    input:
    csv_file: CSV created from filter_table function

    output:
    Check 'outputs' subdirectory in part-3 for boxplot image.

    Create boxplots for each cell population of relative frequencies of
    responders vs. non-responders.
    """
    samp_data = pd.read_csv(csv_file, header=0)

    # plot by cell population, with different colors for response status
    sns.boxplot(samp_data, x='population', y='percentage', hue='response')

    # plot customizations
    plt.title('Immune Response to Miraclib by Melanoma Patients \n(PBMC Samples Only)')
    plt.xlabel('Cell Population')
    plt.ylabel('Relative Frequency (%)')

    # save to 'outputs' subdir
    plt.savefig('./outputs/part-3/freq-boxplot.png')
    plt.clf()
    
    return


def mann_whitney_test(samp_data: pd.DataFrame) -> dict[str, float]:
    """
    input:
    samp_data - dataframe created from filter_table function

    output:
    dictionary of {cell_population: pvalue} results from tests

    Performs Mann-Whitney U tests to determine if there is a 
    significant difference between cell population frequencies
    of responders vs. non-responders. Takes the mean of samples 
    across timepoints to meet independence assumption.
    """
    samp_data['percentage'] = samp_data['percentage'] / 100
    
    # take mean across samples coming from same patient, per population
    samp_means = samp_data.groupby(
            ['patient_id', 'population', 'response']
        )['percentage'].mean().reset_index()
    
    # separate out dataset into responders vs. non-responders
    responder = samp_means[samp_means['response'] == 'yes']
    non_responder = samp_means[samp_means['response'] == 'no']
    results = {}

    # perform Mann-Whitney U test per each cell population
    cell_pops = samp_means['population'].unique()
    for cell in cell_pops:
        u_stat, p_val = mannwhitneyu(
            responder[responder['population'] == cell]['percentage'], 
            non_responder[non_responder['population'] == cell]['percentage'])
        
        results[cell] = p_val

    return results


def check_distr(csv_file: str) -> None:
    """
    input:
    csv_file - CSV file created from filter_table function

    output:
    histograms of responder and non-responder population
    frequency distributions

    See the distribution of responder and non-responder 
    cell population frequencies through plots
    """
    samp_data = pd.read_csv(csv_file, header=0)

    plt.hist(samp_data[samp_data['response'] == 'yes']['percentage'], bins=40)
    plt.title('Distribution of Cell Population Frequencies for Responders')
    plt.xlabel('Cell Population Relative Frequency (%)')
    plt.ylabel('Occurrences')
    plt.savefig('./outputs/part-3/responders-hist.png')
    plt.clf()

    plt.hist(samp_data[samp_data['response'] == 'no']['percentage'], bins=40)
    plt.title('Distribution of Cell Population Frequencies for Non-Responders')
    plt.xlabel('Cell Population Relative Frequency (%)')
    plt.ylabel('Occurrences')
    plt.savefig('./outputs/part-3/non-responders-hist.png')
    plt.clf()

    return


if __name__ == "__main__":
    # the call to the functions below will run with 'make pipeline', and
    # assumes you are in the project root directory (not inside 'outputs' subdir)
    sum_tbl = pd.read_csv('./outputs/part-2/relative-frequencies.csv',
                          header=0)

    # filter table to only get melanoma patients treated with miraclib (PBMC samples)
    filtered_df = filter_table(sum_tbl, 
                    'drug-response.db', 'melanoma', 'miraclib', 'PBMC')
    filtered_df.to_csv('./outputs/part-3/filtered-results.csv', index=False)
    
    # quick comparison of responders vs. non-responders
    summary_stats = filtered_df.rename(columns={'percentage': 'relative_freq'})
    summary_stats = summary_stats.drop(['time_from_treatment_start', 
                                        'total_count', 'count'], axis=1)
    summary_stats['relative_freq'] = summary_stats['relative_freq'] / 100

    # save summary stats of responders vs. non-responders to files
    summary_stats[summary_stats['response'] == 'yes'].groupby(
            'population').describe().reset_index().to_csv(
                './outputs/part-3/responders-stats.csv',
                index=False)
    
    summary_stats[summary_stats['response'] == 'no'].groupby(
            'population').describe().reset_index().to_csv(
                './outputs/part-3/nonresponders-stats.csv',
                index=False)
    
    # create boxplot of population relative freqs of responders vs. non-responders
    create_boxplot('./outputs/part-3/filtered-results.csv')

    # get p-values from Mann-Whitney U tests performed per each cell population
    og_pvals = pd.Series(mann_whitney_test(filtered_df))

    # control FDR and get new adjusted p-values
    corrected_pvals = pd.Series(stats.false_discovery_control(og_pvals, method='bh'),
                                index=og_pvals.index)

    # check which cell populations have a sig difference
    rows = []
    for cell, og_pval in og_pvals.items():
        new_pval = corrected_pvals[cell]

        if new_pval <= 0.05:
            rows.append([cell, og_pval, new_pval, 'yes'])
        else:
            rows.append([cell, og_pval, new_pval, 'no'])

    results = pd.DataFrame(rows, columns=['population', 'original_pval', 
                                          'adjusted_pval', 'significant'])
    results.to_csv('./outputs/part-3/pvals-per-population.csv', index=False)

    # histograms showing distributions of responders vs. non-responders
    check_distr('./outputs/part-3/filtered-results.csv')

    print("See filtered-results.csv in 'outputs' subdirectory for filtered table.")
    print("Boxplots of cell population frequencies saved to freq-boxplot.png.")
    print("Mann-Whitney U test completed for all cell populations.")
    print("Adjusted p-values after Benjamini-Hochberg correction:\n", corrected_pvals)
    print("Please see pvals-per-population.csv for which cell populations are",
          "significantly different between responders and non-responders.\n")