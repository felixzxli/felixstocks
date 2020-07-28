import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas_datareader.data as web
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import requests
import pandas as pd
from urllib.request import Request, urlopen


start = datetime.datetime.today() - relativedelta(years=5)
end = datetime.datetime.today()


def update_news():
    url = "https://finviz.com/news.ashx"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage, "html.parser")
    headlines = []
    links = []
    for article in soup.find_all("tr", class_="nn"):
        # gets the article headline
        content = article.a.text
        # gets the article link
        src = article.a["href"]

        headlines.append(content)
        links.append(src)

    # creates a panda dataframe using a dictionary: assigning value to the headlines and urls
    d = {"headline": headlines, "url": links}
    df = pd.DataFrame(data=d)
    return df


# <tr class="nn" onclick="window.open('https://www.thestreet.com/mishtalk/economics/baseball-season-in-jeopardy-as-marlins-quarantined-in-philadelphia','_blank');return false;">
#                 <td class="news_source_icon is-102" width="20"></td>
#                 <td class="nn-date" width="40" align="center">04:06PM</td>
#                 <td title=""><a href="https://www.thestreet.com/mishtalk/economics/baseball-season-in-jeopardy-as-marlins-quarantined-in-philadelphia" target="_blank" class="nn-tab-link">Baseball Season in Jeopardy as Marlins Quarantined in Philadelphia</a></td>
#             </tr>


def generate_html_table(max_rows=10):
    df = update_news()

    return html.Div(
        [
            html.Div(
                html.Table(
                    # Header
                    [html.Tr([html.Th()])]
                    +
                    # Body
                    [
                        html.Tr(
                            [
                                html.Td(
                                    html.A(
                                        df.iloc[i]["headline"],
                                        href=df.iloc[i]["url"],
                                        target="_blank",
                                    )
                                )
                            ]
                        )
                        for i in range(min(len(df), max_rows))
                    ]
                ),
                style={"height": "300px", "overflowY": "scroll"},
            ),
        ],
        style={"height": "100%"},
    )


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Felix Stocks"
server = app.server
app.layout = html.Div(
    [
        html.Div(
            [
                html.H2("Felix Stockx: Discover The Latest Market Data"),
                html.Img(src="/assets/stock-icon.png"),
            ],
            className="banner",
        ),
        html.Div(
            [
                html.Div(children="""Symbol to graph: (Default S&P 500 Index)"""),
                dcc.Input(id="input", value="SPY", type="text"),
                html.Button(id="submit-button", n_clicks=0, children="Submit"),
            ]
        ),
        html.Div(
            [
                html.Div([dcc.Graph(id="output-graph",)], className="six columns"),
                html.Div(
                    [html.H3("Latest Market News"), generate_html_table()],
                    className="six columns",
                ),
            ],
            className="row",
        ),
    ]
)


# loading = dcc.Loading([
#     # ...
# ])


@app.callback(
    Output("output-graph", "figure"),
    [Input("submit-button", "n_clicks")],
    [State("input", "value")],
)
def update_fig(n_clicks, input_value):
    df = web.DataReader(input_value, "yahoo", start, end)
    df.reset_index(inplace=True)
    df.set_index("Date", inplace=True)

    trace_line = go.Scatter(
        x=list(df.index),
        y=list(df["Close"]),
        # visible=False,
        name="Close",
        showlegend=False,
    )

    trace_candle = go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        # increasing=dict(line=dict(color="#00ff00")),
        # decreasing=dict(line=dict(color="white")),
        visible=False,
        showlegend=False,
    )

    trace_bar = go.Ohlc(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        # increasing=dict(line=dict(color="#888888")),
        # decreasing=dict(line=dict(color="#888888")),
        visible=False,
        showlegend=False,
    )

    data = [trace_line, trace_candle, trace_bar]

    updatemenus = list(
        [
            dict(
                buttons=list(
                    [
                        dict(
                            args=[{"visible": [True, False, False]}],
                            label="Line",
                            method="update",
                        ),
                        dict(
                            args=[{"visible": [False, True, False]}],
                            label="Candle",
                            method="update",
                        ),
                        dict(
                            args=[{"visible": [False, False, True]}],
                            label="Bar",
                            method="update",
                        ),
                    ]
                ),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0,
                xanchor="left",
                y=1.05,
                yanchor="top",
            ),
        ]
    )

    layout = dict(
        title=input_value,
        updatemenus=updatemenus,
        autosize=False,
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
            rangeslider=dict(visible=True),
            type="date",
        ),
    )

    return {"data": data, "layout": layout}


if __name__ == "__main__":
    app.run_server(debug=True)

# price = soup.find_all('div', {'class': 'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text
# returns the graph with an input value as the stock ticker
# def update_value(n_clicks, input_data):
#     start = datetime.datetime(2015, 1, 1)
#     end = datetime.datetime.now()
#     df1 = web.DataReader(input_data, 'yahoo', start, end)
#     df1.reset_index(inplace=True)
#     df1.set_index("Date", inplace=True)

# return dcc.Graph(
#     id='example-graph',
#     figure={
#         'data': [
#             {'x': df1.index, 'y': df1.Close, 'type': 'line', 'name': input_data},
#         ],
#         'layout': {
#             'title': input_data
#         }
#     }
#
# ),
