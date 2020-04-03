
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from datetime import datetime as dt

from apps import sim, tracking
from data import *


# style sheet w/o redo button at bottom left of screen
external_stylesheets = ['/home/tanthiamhuat/DataAnalyticsPortal/UI/mystylesheet.css']

app = dash.Dash(external_stylesheets=external_stylesheets)

# Beanstalk looks for variable: application by default, if this isn't set you will get a WSGI error.
application = app.server
app.config.suppress_callback_exceptions = True  # this line is needed for multi-page apps

# here is the main app.layout variable
app.layout = html.Div([html.H1(children='X8313', style={'text-align': 'left', 'marginBottom': 5}),

                       html.Div(style={'width': '49%', 'display': 'inline-block'},
                                children=[dcc.Link('Tracking', href='/tracking', style={'padding': 5}),
                                          dcc.Link('Simulator', href='/sim')]
                                ),

                       dcc.Location(id='url', refresh=False),
                       html.Div(id='page-content')
                       ]
                      )


# Index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/sim':
        return sim.layout
    elif pathname == '/tracking':
        return tracking.layout
    elif pathname == '/':
        ''
    else:
        return '404'


# if button pressed then re-load data from database
@app.callback(
    Output('electronic_pnl_plot', 'figure'),
    [Input('update_button', 'n_clicks'),
     Input('strategy_dropdown', 'value')])
def update_electronic_pnl_plot(n_clicks, value):
    # required by Dash to be called n_clicks
    if n_clicks != None:
        query()

    return get_electronic_pnl_plot_fig(value)


# select date for PNL Tracking Table
@app.callback(
    Output('tracking_table', 'figure'),
    [Input('date-picker-single', 'date')])
def select_date(date):
    if date is not None:
        date = dt.strptime(date, '%Y-%m-%d').date()
        return get_tracking_table_fig(date)


# entropy filter
@app.callback(
    Output('simulation_plot', 'figure'),
    [Input('entropy_slider', 'value'),
     Input('race_type_checklist', 'values')])
def update_simulation_plot(value, values):
    return simulate_universe(
                        entropy_range=value,
                        race_type=values
                            )


# simulation.py callbacks
@app.callback(
    Output("figure", "figure"),
    [Input("figure-type-dropdown", "value"), Input("submit-button", "n_clicks")]
)
def update_figure(figure_type, n_clicks):
    """
    I want to send data to the backend like this:
    {
        "portfolio1": {
            "strategy1": [
                ('entropy_morning_line_0', 0.85, 0.92),
                ('rank_morning_line_0', 2, 2)
            ],
            "strategy2": [
                ('entropy_morning_line_0', 0.82, 0.98),
                ('rank_morning_line_0', 2, 4),
                ('rebate_pct', 0.4, 0.8)
            ]
        },
        "portfolio2": {
            "strategy1": [
                ('rank_morning_line_0', 2, 2)
            ]
        }
    }

    I think it's a good idea to store this dict somewhere in this
    Module and then edit it as we 
    """
    new_figure = {
        "data": [
            {
                "x": [1, 2, 3, 4, 5],
                "y": [4, 1, 3, 2, 1]
            },
            {
                "x": [1, 2, 3, 4, 5],
                "y": [3.6, 0.8, 3.2, 2.1, 4]
            }
        ],
        "layout": figure_layout
    }

    for i in range(len(new_figure['data'])):
        new_figure['data'][i]['type'] = figure_type

    return new_figure


@app.callback(
    Output('tabs', 'children'),
    [Input('add-portfolio-button', 'n_clicks')]
)
def add_portfolio(n_clicks):
    print("add_portfolio")
    print(n_clicks)

    new_tabs = []
    for n in range(n_clicks + 1):
        new_tabs.append(
            dcc.Tab(style=tab_style, label='Portfolio {}'.format(n+1), value='tab-{}'.format(n+1))
        )
        print(new_tabs)
    return new_tabs


if __name__ == '__main__':
    # AWS Beanstalk expects it to be running on 8080.
    application.run(debug=True, port=8080)
