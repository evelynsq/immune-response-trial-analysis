import sqlite3
import pandas as pd
from dash import Dash, html
import src.summary_table as summary_table
import src.stat_analysis as stat_analysis

app = Dash()

# connect SQLite db and import data
summary_df = summary_table.freq_table('drug-response.db')

# app UI
app.layout = [
    html.Div(children='Dashboard in progress.')
]

if __name__ == '__main__':
    app.run(debug=True)
