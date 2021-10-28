import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import plotly.graph_objects as go
import numpy as np
import process

regions = {}
column_names = []
date = np.array(0)  # Initialize to any data type

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Covid-19 Cases | Namibia"


def app_layouts():
    app.layout = html.Div(
        children=[
            html.Div(
                children=[
                    html.P(children="🦠", className="header-emoji"),
                    html.H1(
                        children="Covid-19 Analysis", className="header-title"
                    ),
                    html.P(
                        children="The novel COVID-19 has devastated and brought economies world-over to a standstill. "
                                 "COVID-19 is a new respiratory virus first identified in Wuhan, Hubei Province, "
                                 "China. Building on your first assignment, this assignment requires you to develop "
                                 "automatic dashboards. The dashboard should allow users to query and customize "
                                 "visualisations.",
                        className="header-description",
                    ),
                ],
                className="header",
            ),
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Div(children="Region", className="menu-title"),
                            dcc.Dropdown(
                                id="region-filter",
                                options=[{"label": r, "value": r} for r in regions.keys()],
                                value="Khomas",
                                clearable=False,
                                className="dropdown",
                            ),
                        ]
                    ),
                    html.Div(
                        children=[
                            html.Div(children="Attribute", className="menu-title"),
                            dcc.Dropdown(
                                id="attribute-filter",
                                options=[{"label": c, "value": c} for c in column_names[1:]],
                                value="Active Cases",
                                clearable=False,
                                # searchable=False,
                                className="dropdown",
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            html.Div(
                                children="Date Range", className="menu-title"
                            ),
                            dcc.DatePickerRange(
                                id="date-range",
                                min_date_allowed=date.min().date(),
                                max_date_allowed=date.max().date(),
                                start_date=date.min().date(),
                                end_date=date.max().date(),
                            ),
                        ]
                    ),
                ],
                className="menu",
            ),
            html.Div(
                children=[
                    html.Div(
                        children=dcc.Graph(
                            id="covid-chart",
                            config={"displayModeBar": False},
                        ),
                        className="card",
                    ),
                ],
                className="wrapper",
            ),
        ]
    )


@app.callback(
    [Output("covid-chart", "figure")],
    [
        Input("region-filter", "value"),
        Input("attribute-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(region, attribute, start_date, end_date):
    reg_data = regions[region]
    mask = ((reg_data['Date'] >= start_date) & (reg_data['Date'] <= end_date))

    filtered_data = reg_data.loc[mask, :]
    bar_graph = go.Figure([go.Scatter(x=filtered_data['Date'], y=filtered_data[attribute],
                                      name=attribute, line=dict(color='#17B897')
                                      )])

    bar_graph.update_traces(line_shape="spline")
    bar_graph.update_layout(title=attribute + ' in ' + region,
                            xaxis_title='Dates', yaxis_title='Covid Cases',
                            plot_bgcolor='#ffffff',
                            )
    bar_graph.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#efefef')
    bar_graph.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#efefef')
    return [bar_graph]


# Import the data from process.py
def data():
    global regions, column_names, date

    process.data()
    regions = process.regions
    column_names = process.column_names
    date = regions['Khomas']['Date']
    print()


if __name__ == "__main__":
    data()
    app_layouts()
    app.run_server(debug=True)
