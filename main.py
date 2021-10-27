import os
import dash
from dash import html
from dash import dcc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

country = None
regions = {}
region_names = []
column_names = []
# Initialize app
app = dash.Dash()


# `end_date - start_date` outputs a stamp e.g `305 days 12:00:00`
# If we convert that to a string, split by spaces, get the first index
# and convert it to int, we get the number of valid days.
# This is because, e.g the 2020 data file contains extra 2021 rows which
# just messes with the whole data structure, thus with valid rows,
# we get the accurate data rows for the year.
# + 1 because end of the year date completes at the start of the year
# or just make `end_date = beginning of the year`
def valid_rows(start_date):
    year = str(start_date)[:4]
    end_date = pd.Timestamp(year + '-12-31')
    rows = int(str(end_date - start_date).split()[0]) + 1
    return rows


def country_wide():
    global country
    global regions

    for region in regions:
        df = regions[region]
        # Initial stage
        if country is None:
            country = df
        else:
            put_date_aside = df['Date']

            # Drop date columns because they cannot be added, only numbers
            df = df.drop('Date', 1)
            country = country.drop('Date', 1)

            # Combine df with country dataframes
            country = country.add(df, fill_value=0)
            country.insert(0, 'Date', put_date_aside)

            temp = country
            print()


def region_wide(sheet, df):
    region_names.append(sheet)
    columns = df.keys()

    # Rename columns to clean names
    for c in columns:
        column = c.strip()
        column_names.append(column)
        df = df.rename(columns={c: c.strip()})

    # Trim dataframe to valid rows
    start_date = df[column_names[0]][0]
    rows = valid_rows(start_date)
    df = df[:rows]

    if sheet in regions:
        regions[sheet] = regions[sheet].append(df, ignore_index=True)
    else:
        regions[sheet] = df


# Read the data from Excel files
def import_data(root):
    files = sorted(os.listdir(root))
    for file in files:
        # Just in case you open an excel file for viewing and never close it,
        # Excel create a temporary file starting with `~$`. Thus exclude such
        # files just in case they exist
        if file.endswith('.xlsx') and not file.startswith('~$'):
            filename = os.path.join(root, file)
            sheets = pd.read_excel(filename, sheet_name=None).keys()
            for sheet in sheets:
                df = pd.read_excel(filename, index_col=None, header=0, sheet_name=sheet)
                # Process data into regions
                if sheet == 'Karas':
                    sheet = 'Kharas'
                region_wide(sheet, df)


# Main driver program
def main():
    import_data('dataset')
    # Process data into country
    country_wide()


# Initialize app layouts
def app_layouts():
    app.layout = html.Div(id='parent', children=[
        html.H1(id='H1', children='Covid-19 Cases',
                style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),

        dcc.Dropdown(id='dropdown',
                     options=[
                         {'label': column_names[1], 'value': column_names[1]},
                         {'label': column_names[2], 'value': column_names[2]},
                         {'label': column_names[3], 'value': column_names[3]},
                         {'label': column_names[4], 'value': column_names[4]},
                         {'label': column_names[5], 'value': column_names[5]},
                         {'label': column_names[6], 'value': column_names[6]},
                         {'label': column_names[7], 'value': column_names[7]},
                         {'label': column_names[8], 'value': column_names[8]},
                     ],
                     value=column_names[1]),
                     # multi=True),
        dcc.Graph(id='bar_plot')
    ])


# Server request functions
@app.callback(Output(component_id='bar_plot', component_property='figure'),
              [Input(component_id='dropdown', component_property='value')])
def graph_update(dropdown_value):
    print(dropdown_value)
    fig = go.Figure([go.Scatter(x=country['Date'], y=country['{}'.format(dropdown_value)],
                                line=dict(color='firebrick', width=4))
                     ])

    fig.update_layout(title='Covid cases in the entire country',
                      xaxis_title='Dates',
                      yaxis_title='Cases'
                      )
    return fig


# Initializer
if __name__ == '__main__':
    # Load data, initialize layouts, run server
    main()
    app_layouts()
    app.run_server()
