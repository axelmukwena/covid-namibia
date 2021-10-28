import os
import dash
from dash import html
from dash import dcc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
import process

regions = {}
column_names = []
# Initialize app
app = dash.Dash()


# Main driver program
def main():
    global regions, column_names

    process.data()
    regions = process.regions
    column_names = process.column_names


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]


# Initialize app layouts
def app_layouts():
    app.title = "Covid-19 Cases | Namibia"

    app.layout = html.Div(id='parent', children=[
        html.H1(id='H1', children='Covid-19 Cases',
                style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),

        dcc.Dropdown(id='dropdown',
                     options=[{'label': k, 'value': k} for k in column_names[1:]],
                     value=column_names[1],
                     # multi=True
                     ),
        dcc.Graph(id='bar_plot')
    ])


# Server request functions
@app.callback(Output(component_id='bar_plot', component_property='figure'),
              [Input(component_id='dropdown', component_property='value')])
def graph_update(dropdown_value):
    print(dropdown_value)
    fig = go.Figure([go.Scatter(x=regions['Khomas']['Date'], y=regions['Khomas']['{}'.format(dropdown_value)],
                                name=dropdown_value
                                )])

    fig.update_traces(line_shape="spline")
    fig.update_layout(title='Covid cases in Khomas region',
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
