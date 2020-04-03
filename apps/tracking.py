# Tracking Report

import dash_core_components as dcc
import dash_html_components as html

from datetime import datetime as dt
from datetime import timedelta as td

from data import *

layout = html.Div(children=[html.H2(children='Tracking', style={'text-align': 'center'}),

                            html.Div(style={'position': 'relative'},
                                     children=[html.Button('Refresh', id='update_button', style={'float': 'left'}),
                                               html.Div(dcc.DatePickerSingle(id='date-picker-single',
                                                                             min_date_allowed=dt(2018, 1, 1),
                                                                             max_date_allowed=dt(2018, 12, 31),
                                                                             initial_visible_month=(dt(2018, 12, 5)).date(),
                                                                             date=(dt(2018, 12, 5)).date()
                                                                             ),
                                                        style={'display': 'inline-block', 'float': 'right'}
                                                        )
                                               ]
                                     ),

                            html.Br(style={'padding': '10px'}),

                            html.Div(style={'position': 'relative', 'height': '400px'},
                                     children=[dcc.Graph(id='electronic_pnl_plot',
                                                         style={'float': 'left', 'width': '60%'}, # 'outline': 'blue solid 1px',
                                                         figure=get_electronic_pnl_plot_fig('Net')
                                                         ),
                                               dcc.Graph(id='tracking_table',
                                                         style={'float': 'left', 'width': '40%'}, # 'outline': 'red solid 1px',
                                                         figure=get_tracking_table_fig((dt(2018, 12, 5)).date()),
                                                         animate=False)
                                               ]
                                     ),

                            dcc.Dropdown(id='strategy_dropdown',
                                         style={'position': 'relative',
                                                'width': '77%'},
                                         options=strategies,
                                         multi=False,
                                         value="Net"
                                         ),

                            html.Br(style={'padding': '10px'})
                            ]
                  )
