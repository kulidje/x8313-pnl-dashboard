# PNL & Risk Management Simulation Environment

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import numpy as np

from data import *

import plotly.plotly as py
import plotly.colors as clrs
import plotly.graph_objs as go
import plotly.tools as tls
import plotly.figure_factory.utils as utils


layout = html.Div(children=[
    html.Div(style={"width": "100%", "height": top_panel_height, "margin-bottom": "0px"}, children=[
        html.Div(style={"width": "{0}%".format(PORTFOLIO_SECTION_WIDTH), "height": "100%", "float": "left", "margin-right": "{0}%".format(PORTFOLIO_SECTION_MARGIN_R)}, children=[
            html.Div(style={"float": "left", "width": "90%"}, children=[
                dcc.Tabs(id="tabs", style={"width": "100%", "height": top_panel_height, "float": "left"}, value='tab-1', children=[
                    dcc.Tab(style=tab_style, label='Portfolio 1', value='tab-1'),
                ]),
            ]),
            html.Button(id="add-portfolio-button", style=add_tab_button_style, children=["+"], n_clicks=0),
        ]),
        html.Div(style={"width": "{0}%".format(BETTING_SECTION_WIDTH), "height": "100%", "float": "left"}, children=[
            # html.Button(id="add-strategy-button", style=small_button_style, children=["+ Strat"]),
            dcc.Dropdown(id="figure-type-dropdown", style=dropdown_style, options=[
                {'label': 'scatter', 'value': 'scatter'},
                {'label': 'bar', 'value': 'bar'},
                {'label': 'box', 'value': 'box'},
                {'label': 'histogram', 'value': 'histogram'},
                {'label': 'scattergl', 'value': 'scattergl'},
                {'label': 'violin', 'value': 'violin'},
            ], value='scatter', searchable=False),
            html.Button(id="delta-lines-button", style=button_style, children=["∆ Lines"]),
            html.Button(id="agg-button", style=button_style, children=["Agg"]),
            html.Button(id="submit-button", style=button_float_right_style, children=["Submit"]),

        ]),
    ]),
    html.Div(id='portfolio-section', style=portfolio_div_style, children=[
        html.Div(style=strategy_style, children=[
            dcc.Input(style=title_style, id="strat-1", type="text", value="Betting Strategy 1"),
            dcc.Input(type="text", placeholder="rebate_pct"), html.Br(),
            dcc.Input(type="text", placeholder="bet_type"), html.Br(),
            dcc.Input(type="text", placeholder="net_return"), html.Br(),
            dcc.Input(type="text", placeholder="payout_norm"), html.Br(),
            dcc.Input(type="text", placeholder="date"), html.Br(),
        ]),
        # html.Div(id="strat-2", style=strategy_style, children=[]),
        html.Button(id="add-strategy-button", style=button_circular_style, children=["+"], n_clicks=0),
    ]),
    html.Div(style=fig_div_style, children=[
        dcc.Graph(
            id="figure",
            style={"margin-top": "10px"},
            figure={
                "data": [{"x": [1, 2, 3, 4, 5], "y": [4, 1, 3, 2, 1]}],
                "layout": figure_layout
            }
        )
    ]),
])
