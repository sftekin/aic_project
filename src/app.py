import os
import shutil
import pandas as pd
import numpy as np
from dash import Dash, Input, Output, dcc, html, State
from dash.exceptions import PreventUpdate
import plotly.express as px

freq_map = {
    "H": "Hourly",
    "D": "Daily",
    "M": "Monthly"
}

data = (pd.read_csv("data/eth_data.csv", parse_dates=["block_timestamp"], index_col=0)
        .set_index("block_timestamp"))
addr_data = pd.read_csv("data/address_data.csv", index_col=0)
id2addr = addr_data["address"].to_dict()
addr2id = addr_data["address"].T.to_dict()


if not os.path.exists(os.path.join("assets", "lib")):
    if not os.path.exists("lib"):
        raise RuntimeError("The lib directory is not found.")
    else:
        shutil.move("lib", "assets/lib")
        print("The lib/ directory is put under assets/")


external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "BERT4ETH: De-anonymization and Phishing Detection"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(children="ETH Account Analytics", className="header-title"),
                html.P(children="Analyze the behavior of accounts", className="header-description")
            ],
            className="header"
        ),
        html.Div(
            children=[
                html.H2(children="Total Transaction Count in each Time Step", className="sub-header")
            ],
            className="subheader"
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Time Frequency", className="menu-title"),
                        dcc.Dropdown(
                            id="freq-filter",
                            options=[{"label": freq_map[freq], "value": freq} for freq in ["H", "D", "M"]],
                            value="D",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range", className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.index.min().date(),
                            max_date_allowed=data.index.max().date(),
                            start_date=data.index.min().date(),
                            end_date=data.index.max().date(),
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
                        id="time-graph",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),

        # De-Anonymization Analysis
        html.Div(
            children=[
                html.H2(children="De-Anonymization Analysis", className="sub-header"),
                html.H3(children="Temporal Analysis", className="subsub-header")
            ],
            className="subheader"
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Time Frequency", className="menu-title"),
                        dcc.Dropdown(
                            id="freq-filter-2",
                            options=[{"label": freq_map[freq], "value": freq} for freq in ["H", "D", "M"]],
                            value="H",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="The First Account Address", className="menu-title"),
                        dcc.Input(
                            placeholder='e.g. 0x0000000000000000000000000000000000000000',
                            type='text',
                            value='',
                            id="account-filter-1",
                            size="40",
                            className="search-bar"
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="The Second Account Address", className="menu-title"),
                        dcc.Input(
                            placeholder='e.g. 0x0000000000000000000000000000000000000001',
                            type='text',
                            value='',
                            id="account-filter-2",
                            size="40",
                            className="search-bar"
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
                        id="deanony-graph",
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
                        id="hourly-graph",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="weekly-graph",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
        html.Div(
            children=[
                html.H3(children="Spatial Analysis", className="subsub-header")
            ],
            className="subheader"
        ),
        html.Div(
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
            children=[
                html.Div(dcc.Input(id='input-on-submit1', type='text', placeholder="First Account")),
                html.Div(dcc.Input(id='input-on-submit2', type='text', placeholder="Second Account")),
                html.Button(id='add-element-button', n_clicks=0, children='Create graph',
                            style={"width": '200px'}),
            ],
            className="menu"
        ),
        html.Div(id="graph-layout"),

        # Phishing
        html.Div(
            children=[
                html.H2(children="Phishing Analysis", className="sub-header"),
                html.H3(children="Temporal Analysis", className="subsub-header")
            ],
            className="subheader"
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Time Frequency", className="menu-title"),
                        dcc.Dropdown(
                            id="freq-filter-3",
                            options=[{"label": freq_map[freq], "value": freq} for freq in ["H", "D", "M"]],
                            value="H",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="The Phishing Account Address", className="menu-title"),
                        dcc.Input(
                            placeholder='e.g. 0x0000000000000000000000000000000000000001',
                            type='text',
                            value='',
                            id="account-filter-3",
                            size="40",
                            className="search-bar"
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
                        id="phishing-graph",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
        html.Div(
            children=[
                html.H3(children="Spatial Analysis", className="subsub-header")
            ],
            className="subheader"
        ),
        html.Div(
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
            children=[
                html.Div(dcc.Input(id='input-on-submit3', type='text', placeholder="Phishing Account")),
                html.Button(id='add-element-button2', n_clicks=0, children='Create graph',
                            style={"width": '200px'}),
            ],
            className="menu"
        ),
        html.Div(id="graph-layout2"),
    ]
)


@app.callback(
    Output("time-graph", "figure"),
    Input("freq-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_time_plot(freq, start_date, end_date):
    fil_data = data.groupby(pd.Grouper(freq=freq)).count()
    fil_data = fil_data.loc[(fil_data.index > start_date) & (fil_data.index < end_date)]
    time_plot_figure = {
        "data": [
            {
                "x": fil_data.index,
                "y": fil_data["hash"],
                "type": "lines",
            },
        ]
    }
    return time_plot_figure


# Deanony FUNCTIONS
@app.callback(
    Output("deanony-graph", "figure"),
    Input("freq-filter-2", "value"),
    Input("account-filter-1", "value"),
    Input("account-filter-2", "value"),
)
def update_deanony_time_plot(freq, addr_1, addr_2):
    addr_df_1 = process_addr(addr_1, freq)
    addr_df_2 = process_addr(addr_2, freq)

    time_plot_figure = {
        "data": [
            {
                "x": addr_df_1.index,
                "y": addr_df_1["hash"],
                "type": "lines",
                "name": addr_1,
                "marker": dict(color='rgb(55, 83, 109)'),
            },
            {
                "x": addr_df_2.index,
                "y": addr_df_2["hash"],
                "type": "lines",
                "name": addr_2,
                "marker": dict(color='rgb(26, 118, 255)'),
            },
        ]
    }
    return time_plot_figure


@app.callback(
    Output("hourly-graph", "figure"),
    Input("account-filter-1", "value"),
    Input("account-filter-2", "value"),
)
def update_deanony_acc_hourly_plot(addr_1, addr_2):
    addr_df_1 = process_addr(addr_1, freq="H")
    addr_df_2 = process_addr(addr_2, freq="H")

    arr_1 = get_daily_trend(addr_df_1)
    arr_2 = get_daily_trend(addr_df_2)

    account_df1 = pd.DataFrame({"time_step": np.arange(24), "tx_count": arr_1, "address": np.tile(addr_1, 24)})
    account_df2 = pd.DataFrame({"time_step": np.arange(24), "tx_count": arr_2, "address": np.tile(addr_2, 24)})
    deanony_df = pd.concat([account_df1, account_df2])

    fig = px.bar(deanony_df, x="time_step", y="tx_count",
                 color="address", barmode='overlay',
                 title="Daily Trend of the Accounts", labels={'x': 'Hour intervals', 'y': 'TX Count'})

    layout = dict(
        xaxis=dict(
            tickmode="array",
            tickvals=np.arange(0, 24).astype(int),
        )
    )

    fig.update_layout(layout)

    return fig


@app.callback(
    Output("weekly-graph", "figure"),
    Input("account-filter-1", "value"),
    Input("account-filter-2", "value"),
)
def update_deanony_acc_weekly_plot(addr_1, addr_2):
    addr_df_1 = process_addr(addr_1, freq="D")
    addr_df_2 = process_addr(addr_2, freq="D")

    arr_1 = get_weekly_trend(addr_df_1)
    arr_2 = get_weekly_trend(addr_df_2)

    account_df1 = pd.DataFrame({"time_step": np.arange(7), "tx_count": arr_1, "address": np.tile(addr_1, 7)})
    account_df2 = pd.DataFrame({"time_step": np.arange(7), "tx_count": arr_2, "address": np.tile(addr_2, 7)})
    deanony_df = pd.concat([account_df1, account_df2])

    fig = px.bar(deanony_df, x="time_step", y="tx_count",
                 color="address", barmode='overlay',
                 title="Weekly Trend of the Accounts", labels={'x': 'Day intervals', 'y': 'TX Count'})

    layout = dict(
        xaxis=dict(
            tickmode="array",
            tickvals=np.arange(0, 7).astype(int),
        )
    )

    fig.update_layout(layout)

    return fig


@app.callback(
    Output('graph-layout', 'children'),
    Input('add-element-button', 'n_clicks'),
    State('input-on-submit1', 'value'),
    State('input-on-submit2', 'value')
)
def add_strategy_divison(n_clicks, first_addr, second_addr):
    if n_clicks:
        element = html.Div(
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
            children=[
                html.Iframe(src="assets/deanon_2288_826827.html",
                            style={"height": "512px", "width": "600px"}
                            )
            ]
        )
        return element
    else:
        raise PreventUpdate


# Phishing FUNCTIONS
@app.callback(
    Output("phishing-graph", "figure"),
    Input("freq-filter-3", "value"),
    Input("account-filter-3", "value"),
)
def update_deanony_time_plot(freq, addr):
    account_df = process_addr(addr, freq)
    time_plot_figure = {
        "data": [
            {
                "x": account_df.index,
                "y": account_df["hash"],
                "type": "lines",
                "name": addr,
                "marker": dict(color='rgb(55, 83, 109)'),
            }
        ]
    }
    return time_plot_figure


@app.callback(
    Output('graph-layout2', 'children'),
    Input('add-element-button2', 'n_clicks'),
    State('input-on-submit3', 'value'),
)
def add_strategy_divison(n_clicks, phis_addr):
    if n_clicks:
        element = html.Div(
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
            children=[
                html.Iframe(src="assets/phish_label_2294.html",
                            style={"height": "512px", "width": "600px"}
                            )
            ]
        )
        return element
    else:
        raise PreventUpdate


def process_addr(addr_str, freq="H"):
    addr_df = data.loc[data["from_address"] == addr_str]
    addr_df = addr_df.groupby(pd.Grouper(freq=freq)).count()
    return addr_df


def get_daily_trend(acc_df):
    daily_tx_count = []
    for time_ind in range(24):
        idx = pd.to_datetime(acc_df.index).hour == time_ind
        daily_tx_count.append(acc_df.loc[idx, "hash"].sum())
    return daily_tx_count


def get_weekly_trend(acc_df):
    weekly_tx_count = []
    for time_ind in range(7):
        idx = pd.to_datetime(acc_df.index).dayofweek == time_ind
        weekly_tx_count.append(acc_df.loc[idx, "hash"].sum())
    return weekly_tx_count


if __name__ == "__main__":
    app.run_server(debug=True)
