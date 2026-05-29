import pandas as pd
from dash import Dash, dash_table, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from scipy import stats
import src.summary_table as summary_table
import src.stat_analysis as stat_analysis

app = Dash(__name__, external_stylesheets = [dbc.themes.LUX])

#### Import Data
# Part 2 summary table
pt2_summary_df = summary_table.freq_table('drug-response.db')

# Part 3 filtered frequency table for melanoma miraclib patients (PBMC only)
pt3_filtered_df = stat_analysis.filter_table(pt2_summary_df, 
                    'drug-response.db', 'melanoma', 'miraclib', 'PBMC')

# Part 3 p-values from Mann-Whitney U tests performed per each cell population
og_pvals = pd.Series(stat_analysis.mann_whitney_test(pt3_filtered_df))

# Part 3 new adjusted p-values from controlling FDR
corrected_pvals = pd.Series(stats.false_discovery_control(og_pvals, method='bh'),
                            index=og_pvals.index)

# Part 4 table of all melanoma PBMC samples at baseline from miraclib patients
pt4_all_samples = pd.read_csv('./outputs/part-4/initial-query-data.csv')


#### App UI
app.layout = dbc.Container([

    # Dashboard Title Row
    dbc.Row([
        dbc.Col(
            html.H3(
                'Immune Cell Population Analysis Results',
                style={
                    'text-align': 'center',
                    'padding': '20px 0 10px 0'
                }
            ), width=12,
            style={'backgroundColor': '#f5efef'})
    ]),

    html.Br(),

    # Part 2: Data Overview Results Row
    dbc.Row([
        dbc.Col([
            html.H5('Part 2: Relative Frequencies Overview'),

            html.P('The following data shows the relative frequencies of each ' \
                'cell population per sample.'),

            # relative frequencies table
            dash_table.DataTable(
                id='pt2-freq-table',
                data=pt2_summary_df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in pt2_summary_df.columns],
                page_size=12,
                filter_action='native',
                sort_action='native',
                style_table={
                    'overflowX': 'auto',
                },
                style_cell={
                    'padding': '6px',
                    'fontSize': '12px'
                }
            ),

            # dynamically update num of rows filtered for in data table
            html.Div(id='pt2-num-rows', style={'text-align': 'right'})

        ], width=12, style={'margin': '5px',
                            'text-align': 'center'})
    ], className='mb-4'),


    # Part 3: Statistical Analysis Plots Row
    dbc.Row([
        html.H5('Part 3: Statistical Analysis', 
                style={'text-align': 'center'}),

        html.P('Comparison of differences in cell population relative frequencies of ' \
        'responder vs. non-responder melanoma patients receiving miraclib (PBMC samples only).'),
        
        # boxplot of population frequencies
        dbc.Col([
            dcc.Graph(id='pt3-boxplot-fig')
        ], width=6),

        # histogram of population frequencies
        dbc.Col([
            dcc.Graph(id='pt3-histogram-fig')
        ], width=6),

        # checklist for filtering plots by response status
        dcc.Checklist(
            id='pt3-checklist',
            options=['Responders', 'Non-Responders'],
            value=['Responders', 'Non-Responders'],
            inline=True
        )

    ], className='mb-4', style={'text-align': 'center',
                                'display': 'flex',
                                'justifyContent': 'center'}),


    # Part 3: Statistical Test Row
    dbc.Row([
        html.P('Below are the results of performing a Mann-Whitney U test per each cell population ' \
            'to determine whether the relative frequencies of responders vs. non-responders have ' \
            'a significant difference. P-values are adjusted afterwards for FDR control using the ' \
            'Benjamini-Hochberg procedure.',
            style={'padding': '10px 0 10px 0'}),
        
        # results of Mann-Whitney U test
        dbc.Col([
            # slider to input FDR
            dcc.Slider(
                id='pt3-fdr-slider',
                min=0,
                max=0.25,
                step=0.01,
                value=0.05,
            ),
            
            # data table that will populate with results of test
            dash_table.DataTable(
                id='pt3-test-results',
                columns=[{'name': i, 'id': i} for i in 
                         ['population', 'original_pval', 'adjusted_pval', 
                          'significant']],
                page_size=12,
                filter_action='native',
                sort_action='native',
                style_table={
                    'overflowX': 'auto',
                    'padding-top':'35px',
                    'padding-bottom':'30px'
                },
                style_cell={
                    'padding': '6px',
                    'fontSize': '12px'
                }
            )
        ], width=6),

        html.P("With an FDR cutoff of 0.05, we cannot conclude a statistically significant " \
            "difference for any of the cell types' relative frequencies when comparing responders vs. " \
            "non-responders (for melanoma patients treated with miraclib, PBMC samples only). ",
            style={'padding': '10px 0 10px 0'}),

    ], className='mb-4', style={'text-align': 'center',
                                'padding': '10px 0 10px 0',
                                'display': 'flex',
                                'justifyContent': 'center'}),

    html.Br(),

    # Part 4: Data Subset Analysis
    dbc.Row([
        dbc.Col([
            html.H5('Part 4: Data Subset Analysis', style={'text-align': 'center'}),

            html.P('Data for all melanoma PBMC samples at baseline (t=0), ' \
            'from patients treated with miraclib.'),

            # dropdown to filter by available projects
            dcc.Dropdown(
                id='pt4-dropdown',
                options=pt4_all_samples['project_id'].unique(),
                multi=True,
                placeholder='Filter by project...',
                style={'width': '15%', 
                       'padding-bottom':'5px'}
            ),

            # data table from part 4's initial query
            dash_table.DataTable(
                id='pt4-samp-table',
                data=pt4_all_samples.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in pt4_all_samples.columns],
                page_size=12,
                filter_action='native',
                sort_action='native',
                style_table={
                    'overflowX': 'auto',
                },
                style_cell={
                    'padding': '6px',
                    'fontSize': '12px'
                }
            ),

            html.Div(id='pt4-num-rows', style={'text-align': 'right'})

        ], width=12, style={'margin': '5px',
                            'text-align': 'center'})

    ]),

    html.Br()
    
], fluid=True, style={'padding-bottom': '20px'})


#### App callback functions
# Count number of rows in data table before/after filtering - part 2
@app.callback(
    Output('pt2-num-rows', 'children'),
    Input('pt2-freq-table', 'derived_virtual_data')
)
def count_pt2_rows(filtered_rows):
    if filtered_rows is None:
        return str(len(pt2_summary_df)) + ' samples'
    else:
        return str(len(filtered_rows)) + ' samples'
    
# Update boxplot with responder and/or non-responder data based on 
# checklist input - part 3
@app.callback(
    Output('pt3-boxplot-fig', 'figure'),
    Input('pt3-checklist', 'value')
)
def create_boxplot(checked_items):
    # map the checked response statuses to their value in the table
    selected_vals = []
    for item in checked_items:
        if item == 'Responders':
            selected_vals.append('yes')
        elif item == 'Non-Responders':
            selected_vals.append('no')

    # filter df based on response status(es) selected
    if not checked_items:
        plot_df = pt3_filtered_df.iloc[0:0]
    else:
        plot_df = pt3_filtered_df[
            pt3_filtered_df['response'].isin(selected_vals)]

    return px.box(
        plot_df,
        x='population',
        y='percentage',
        color='response',
        points='all',
        title='Immune Response by Cell Population',
        labels={'percentage': 'Relative Frequency (%)',
                'population': 'Cell Population'},
        height=600)

# Update histogram with responder and/or non-responder data based on 
# checklist input - part 3
@app.callback(
    Output('pt3-histogram-fig', 'figure'),
    Input('pt3-checklist', 'value')
)
def create_boxplot(checked_items):
    # map the checked response statuses to their value in the table
    selected_vals = []
    for item in checked_items:
        if item == 'Responders':
            selected_vals.append('yes')
        elif item == 'Non-Responders':
            selected_vals.append('no')

    # filter df based on response status(es) selected
    if not checked_items:
        plot_df = pt3_filtered_df.iloc[0:0]
    else:
        plot_df = pt3_filtered_df[
            pt3_filtered_df['response'].isin(selected_vals)]

    return px.histogram(
        plot_df,
        x='percentage',
        color='response',
        barmode='group',
        nbins=40,
        opacity=1,
        title='Distribution of Cell Population Frequencies',
        labels={'percentage': 'Cell Population Relative Frequency (%)'},
        height=600)

# Check which cell pops have a sig difference based on adjusted pvals - part 3
@app.callback(
    Output('pt3-test-results', 'data'),
    Input('pt3-fdr-slider', 'value')
)
def pt3_stat_test(fdr):
    rows = []
    for cell, og_pval in og_pvals.items():
        new_pval = corrected_pvals[cell]

        if new_pval <= fdr:
            rows.append([cell, og_pval, new_pval, 'yes'])
        else:
            rows.append([cell, og_pval, new_pval, 'no'])

    results = pd.DataFrame(rows, columns=['population', 'original_pval', 
                                          'adjusted_pval', 'significant'])

    return results.to_dict('records')

# Count number of rows in data table before/after filtering - part 4
@app.callback(
    Output('pt4-num-rows', 'children'),
    Input('pt4-samp-table', 'derived_virtual_data')
)
def count_pt4_rows(filtered_rows):
    if filtered_rows is None:
        return str(len(pt4_all_samples)) + ' samples'
    else:
        return str(len(filtered_rows)) + ' samples'

# Filter table based on project id(s) selected - part 4
@app.callback(
    Output('pt4-samp-table', 'data'),
    Input('pt4-dropdown', 'value')
)
def filter_project(selected_projs):
    if not selected_projs:
        return pt4_all_samples.to_dict('records')
    else:
        filtered_df = pt4_all_samples[pt4_all_samples['project_id'].isin(selected_projs)]
        return filtered_df.to_dict('records')
        

#### Run App
if __name__ == '__main__':
    app.run(debug=True)
