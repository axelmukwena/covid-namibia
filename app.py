import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import plotly.graph_objects as go
import random
import process

regions = {}
column_names = []
date = None  # Initialize to any data type

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
                    html.Div(className='column',
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
                    html.Div(className='column',
                             children=[
                                 html.Div(children="Attribute", className="menu-title"),
                                 dcc.Dropdown(
                                     id="attribute-filter",
                                     options=[{"label": c, "value": c} for c in column_names if c != 'Date'],
                                     value="Active Cases",
                                     clearable=False,
                                     # searchable=False,
                                     className="dropdown",
                                 ),
                             ],
                             ),
                    html.Div(className='column',
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
            html.Div(className='content',
                     children=[
                         html.Div(
                             children=[
                                 html.Div(
                                     children=dcc.Graph(
                                         id="line-chart",
                                         config={"displayModeBar": False},
                                     ),
                                     className="card",
                                 ),
                             ],
                             className="wrapper",
                         ),
                         html.Div(
                             children=[
                                 html.Div(
                                     children=dcc.Graph(
                                         id="bar-chart",
                                         config={"displayModeBar": False},
                                     ),
                                     className="card",
                                 ),
                             ],
                             className="wrapper",
                         ),
                         html.Div(
                             children=[
                                 html.Div(
                                     children=dcc.Graph(
                                         id="pie-chart",
                                         config={"displayModeBar": False},
                                     ),
                                     className="card",
                                 ),
                             ],
                             className="wrapper",
                         ),
                     ]
            )
        ]
    )


# Create random color
# https://stackoverflow.com/questions/28999287/generate-random-colors-rgb#comment104784319_50218895
def rgb():
    color = f"#{random.randrange(0x1000000):06x}"
    return color


def bar(filtered_data, column):
    b = go.Bar(
        x=filtered_data['Date'],
        y=filtered_data[column],
        name=column,
        marker=dict(color=rgb())
    )
    return b


@app.callback(
    [
        Output("line-chart", "figure"),
        Output("bar-chart", "figure"),
        Output("pie-chart", "figure")
    ],
    [
        Input("region-filter", "value"),
        Input("attribute-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_line_graph(region, attribute, start_date, end_date):
    reg_data = regions[region]
    mask = ((reg_data['Date'] >= start_date) & (reg_data['Date'] <= end_date))
    filtered_data = reg_data.loc[mask, :]

    # Line graph
    line_graph = go.Figure([go.Scatter(x=filtered_data['Date'], y=filtered_data[attribute],
                                       name=attribute, line=dict(color='#17B897')
                                       )])
    line_graph.update_traces(line_shape="spline")
    line_graph.update_layout(title='Line Graph for ' + attribute + ' in ' + region,
                             xaxis_title='Dates per Day', yaxis_title='Covid Cases',
                             plot_bgcolor='#ffffff',
                             )
    line_graph.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#efefef')
    line_graph.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#efefef')

    # Stacked Bar graph
    # df.resample converts the column used to index column, so convert back
    resampled_data = filtered_data.resample('M', on='Date').sum()
    # https://stackoverflow.com/a/54276300/8050183
    resampled_data = resampled_data.rename_axis('Date').reset_index()
    bar_graph = go.Figure(data=[bar(resampled_data, c) for c in column_names[1:]])
    bar_graph.update_layout(title='Stacked Bar Graph for ' + region,
                            barmode='stack', xaxis_title='Dates per Month (Click/double click right menu to toggle '
                                                         'visibility)',
                            yaxis_title='Covid Cases',
                            plot_bgcolor='#ffffff',
                            )
    bar_graph.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#efefef')
    bar_graph.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#efefef')

    # Pie Chart
    # This creates a series, then we iterate through the series
    # to get labels and values
    pie_data = filtered_data.sum(numeric_only=True)
    labels, values = [], []
    [(labels.append(i[0]), values.append(i[1])) for i in pie_data.items()]
    pie_chart = go.Figure([go.Pie(labels=labels, values=values)])
    pie_chart.update_layout(title='Pie Chart for ' + region)

    return [line_graph, bar_graph, pie_chart]


# Import the data from process.py
def data():
    global regions, column_names, date

    # To process data from  `dataset/raw`, uncomment the line below, and comment `process.read_data()`
    # process.process_data()
    process.read_data()  # Read processed data
    regions = process.regions
    column_names = process.column_names
    date = regions['Khomas']['Date']


data()
app_layouts()

if __name__ == "__main__":
    app.run_server(debug=True)
