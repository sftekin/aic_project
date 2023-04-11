import os
import pandas as pd
from dash import Dash, Input, Output, dcc, html

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
                html.P(children="Analyze the behavior of an account", className="header-description")
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
                            value="H",
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

        html.Div(
            children=[
                html.H2(children="De-Anonymization Analysis", className="sub-header")
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


@app.callback(
    Output("deanony-graph", "figure"),
    Input("freq-filter-2", "value"),
    Input("account-filter-1", "value"),
    Input("account-filter-2", "value"),
)
def update_deanony_plot(freq, addr_1, addr_2):
    def process_addr(addr_str):
        addr_df = data.loc[data["from_address"] == addr_str]
        addr_df = addr_df.groupby(pd.Grouper(freq=freq)).count()
        return addr_df

    addr_df_1 = process_addr(addr_1)
    addr_df_2 = process_addr(addr_2)

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


if __name__ == "__main__":
    app.run_server(debug=True)
