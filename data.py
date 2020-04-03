import plotly.graph_objs as go

import pandas as pd
import os

from datetime import datetime as dt
from datetime import timedelta as td

# global directories
path_dir = os.path.dirname(__file__)
path_data = os.path.join(path_dir, 'data')


# query database
def query():
    global actual_pnl, simulated_pnl, actual_electronic_pnl, actual_web_pnl, strategies
    print('querying database..')

    # data
    path_simulated_pnl = os.path.join(path_data, 'simulated_pnl_2018.csv')
    simulated_pnl = pd.read_csv(path_simulated_pnl, parse_dates=['date'])
    # filter out bets that were not accepted
    simulated_pnl = simulated_pnl[simulated_pnl.serial_number.notnull()]

    # path to reports data
    path_reports = os.path.join(path_data, 'reports_2018.csv')
    # reports dataframe
    actual_pnl = pd.read_csv(path_reports, parse_dates=['date'])

    # set of serial numbers from simulated df
    electronic_serials = simulated_pnl.serial_number.values
    # get the set of serial numbers that only exist in the reports
    web_serials = list(set(actual_pnl.serial_number) - set(electronic_serials))

    # get the reports pnl of all bets from simulated df
    actual_electronic_pnl = actual_pnl[actual_pnl['serial_number'].isin(electronic_serials)]
    # get the reports pnl of all reports bets that do not exist in simulated df
    actual_web_pnl = actual_pnl[actual_pnl['serial_number'].isin(web_serials)]

    strategies = [{'label': label, 'value': label} for label in simulated_pnl['strategy_name'].unique()]
    strategies.append({'label': 'Net', 'value': 'Net'})


# give Dash the data in-memory
query()


# Historical PNL Plot (Electronic Bets)
def get_electronic_pnl_plot_fig(strategy_name):

    dates = pd.date_range(actual_pnl['date'].min(), actual_pnl['date'].max())

    if strategy_name == 'Net':
        nr_actuals = dates.map(lambda x: actual_electronic_pnl.groupby('date').net_return.sum().get(x))
        nr_simulations = dates.map(lambda x: simulated_pnl.groupby('date').net_return.sum().get(x))
    else:
        target_serials = simulated_pnl[simulated_pnl['strategy_name'] == strategy_name]['serial_number'].values

        nr_actuals = dates.map(lambda x: actual_electronic_pnl[actual_electronic_pnl['serial_number'].isin(target_serials)].groupby('date').net_return.sum().get(x))
        nr_simulations = dates.map(lambda x: simulated_pnl[simulated_pnl['serial_number'].isin(target_serials)].groupby('date').net_return.sum().get(x))

    # actual
    trace0 = go.Bar(
        x=dates,
        y=nr_actuals,
        #mode='lines+markers',
        name='actuals'
    )

    # simulated
    trace1 = go.Bar(
        x=dates,
        y=nr_simulations,
        #mode='lines+markers',
        name='simulations'
    )

    # axis scaling (for layout)
    buffer = 10
    days = 7

    data = [trace0, trace1]
    layout = {'legend': {'x': 0.89},
              'margin': {'l': 40, 'r': 10, 'b': 22},
              'xaxis': {
                  # 'range': [dates[-days] - td(hours=12), dates[-1] + td(hours=12)],
                  'autorange': True
              },
              'yaxis': {
                  # 'range': [nr_actuals[-days:].min() - buffer, nr_actuals[-days:].max() + buffer],
                  'autorange': True
              },
              'dragmode': 'pan'
              }

    figure = dict(data=data, layout=layout)

    return figure


# TODO put this somewhere
# Historical PNL Plot (Web Placed Bets)
def get_web_pnl_plot_fig():

    dates = pd.date_range(actual_pnl['date'].min(), actual_pnl['date'].max())

    nr_actuals = dates.map(lambda x: actual_web_pnl.groupby('date').net_return.sum().get(x)).fillna(0)

    # actual
    trace0 = go.Scatter(
        x=dates,
        y=nr_actuals,
        mode='lines+markers',
        name='web placed actual pnl'
    )

    data = [trace0]
    layout = {'legend': {'x': 0.89},
              'margin': {'l': 35, 'r': 10}
              }

    figure = dict(data=data, layout=layout)

    return figure


# Tracking Table
def get_tracking_table_fig(target_date):
    # tracking report for yesterday by strategies executed

    # create data set from data
    pnl = pd.merge(actual_pnl, simulated_pnl, on='serial_number', how='left', suffixes=['_actual', '_sim'])

    # get target date
    pnl = pnl[pnl.date_actual.dt.date == target_date]

    # groupby strategy and sum net return then round to 2 decimals
    target_pnl = pnl.groupby('strategy_name').sum()[['net_return_actual', 'net_return_sim']].applymap(lambda x: round(x, 2))

    # compute difference between actual and simulated return then round to 2 decimals
    target_pnl['delta_pct'] = (target_pnl['net_return_actual'] - target_pnl['net_return_sim']) / target_pnl['net_return_actual']
    target_pnl['delta_pct'] = target_pnl['delta_pct'].map(lambda x: round(x, 2))

    target_pnl = target_pnl.reset_index()

    # set title equal to something for layout variable later on
    date_string = target_date.strftime('%Y/%m/%d')
    if target_pnl.empty:
        title = '%s (No Bets)' % date_string
    else:
        title = date_string

    # color scheme: Reds
    colors = ['rgb(255,246,242)', 'rgb(222,45,38)']
    # if the % difference of actual pnl and simulated pnl is greater than 3%, then shade the row with dark red.
    target_pnl['Color'] = target_pnl['delta_pct'].map(lambda x: colors[0] if abs(x) < 0.03 else colors[1])
    # choose columns to show on web page
    shown_columns = ['strategy_name', 'net_return_actual', 'net_return_sim', 'delta_pct']

    # make table figure
    trace0 = go.Table(
        header=dict(
            values=shown_columns,
            line=dict(color='white'),
            fill=dict(color='white'),
            align=['center'],
            font=dict(color='black', size=12)
        ),
        cells=dict(
            values=[target_pnl[c] for c in shown_columns],
            line=dict(color=[target_pnl.Color]),
            fill=dict(color=[target_pnl.Color]),
            align='center',
            font=dict(color='black', size=11)
        ))

    data = [trace0]

    layout = dict(title=title,
                  margin=dict(r=20, l=20))

    fig = dict(data=data, layout=layout)

    return fig


dtype = {'num_iv_score_total_1': int,
         'race_race_type': 'category',
         'payout_norm': float,
         'x8_track_sym': 'category',
         'num_iv_score_total_0': float,
         'tradingprofitloss': float,
         'race_id': str,
         'iv_score_total_0': int,
         'pool_total': float,
         'name_0': str,
         'num_iv_score_total_3': int,
         'date': str,
         'iv_score_jockey_0': int,
         'x8race_class_0': 'category',
         'net_return': float,
         'iv_score_trainer_0': int,
         'rank_morning_line_0': int,
         'num_iv_score_total_2': int,
         'correct_money': float,
         'bet_type': 'category',
         'refunds': float,
         'rebate_pct': float,
         'entropy_morning_line_0': float,
         'iv_score_median_runner_HDWPSRRating_0': float}

# print('reading df_universe..')
# dfs = []
# for year in range(2015, 2020):
#     fp_web = os.getcwd()
#     fp_target = os.path.join(fp_web, 'data/pnl.df_%s03.csv' % year)
#     _df = pd.read_csv(fp_target, dtype=dtype, parse_dates=['date'])
#     dfs.append(_df)
#
# df_universe = pd.concat(dfs)


# STRATEGY CODE
# def make_criteria_between(attr, minval, maxval):
#     return {'crit_between_{}_{}__{}'.format(attr, minval, maxval): lambda df: df[df[attr].between(minval, maxval)]}
#
#
# def make_criteria_isin(attr, list_valid):
#     return {'crit_isin_{}_{}'.format(attr, '.'.join(list_valid)): lambda df: df[df[attr].isin(list_valid)]}
#
#
# def merge_dicts(*dict_args):
#     """
#     Given any number of dicts, shallow copy and merge into a new dict,
#     precedence goes to key value pairs in latter dicts.
#     - normally some combination of make_criteria_between() and make_criteria_isin()
#     """
#     result = {}
#     for dictionary in dict_args:
#         result.update(dictionary)
#     return result
#
#
# crit_ml_ent = make_criteria_between('entropy_morning_line_0', 0.85, 0.92)
# crit_ml_rank = make_criteria_between('rank_morning_line_0', 2, 2)
#
# target_strategy = merge_dicts(crit_ml_ent, crit_ml_rank)
#
#
# def apply_criteria(df, dict_crit):
#     # apply dicts in dict_crit
#     # Applies criteria to filter runners in df'
#     # i.e.'x8is_par_HDWPSRRating': lambda df:df[df['x8is_HDWPSRRating_norm_par']>0]
#
#     for crit_name, crit_func in dict_crit.items():
#         df = crit_func(df)
#     return df
#
#
# def simulate(date, strategy):
#     # all races in March before target_date since 2015
#     df_sim = apply_criteria(df_universe[df_universe['date'] < date], strategy)
#
#     sim_base = len(df_sim) - df_sim.refunds.sum()
#     sim_nr = df_sim.net_return.sum()
#     sim_roi = round(sim_nr / sim_base, 2)
#     print('simulate(): %s days' % df_sim.date.nunique())
#     return sim_roi
#
#
# def actual(date, strategy):
#     # actual returns of strategy applied to target_date
#     df_act = apply_criteria(df_universe[df_universe['date'] == date], strategy)
#
#     act_base = len(df_act) - df_act.refunds.sum()
#     act_nr = df_act.net_return.sum()
#     act_roi = round(act_nr / act_base, 2)
#     print('actual(): %s days' % df_act.date.nunique())
#     return act_roi
#
#
# def simulate_universe(strategy=target_strategy):
#     # X
#     dates = pd.date_range(dt(2019, 3, 1), dt(2019, 3, 14))
#     # Y
#     sim = dates.map(lambda x: simulate(x, strategy)).values
#     act = dates.map(lambda x: actual(x, strategy)).values
#
#     # sim
#     trace0 = go.Scatter(
#         x=dates,
#         y=sim,
#         mode='lines',
#         name='sim'
#     )
#
#     # act
#     trace1 = go.Scatter(
#         x=dates,
#         y=act,
#         mode='lines',
#         name='act'
#     )
#
#     data = [trace0, trace1]
#     layout = {'yaxis': {'range': [-1, 1]}}
#
#     figure = dict(data=data, layout=layout)
#
#     return figure


# variables for sim
color1 = "#3AAFA9"
color2 = "#2B7A78"
color3 = "#17252A"
white1 = "#DEF2F1"
white2 = "#FEFFFF"
strategy_bkgd = "rgba(255,255,255,0.8)"

dashboard_height = "600px"
border_radius = "2px"
width = "8"
top_panel_height = "50px"
figure_width = "80"

# a handful of strategy rules that are useful
strategy_rules = ["rebate_pct", "date", "bet_type", "net_return", "payout_norm"]
PORTFOLIOS = {
    'portfolio1': {
        zip(strategy_rules, [""] * len(strategy_rules))
    },
    'portfolio2': {
        zip(strategy_rules, [""] * len(strategy_rules))
    }
}

# we want to store the users' portfolios and temp data here
example_all_portfolios = {
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

########################
# MASTER WINDOW VALUES #
########################
PORTFOLIO_SECTION_WIDTH = 24
PORTFOLIO_SECTION_MARGIN_R = 1
# BETTING_SECTION_WIDTH = 69
BETTING_SECTION_WIDTH = 100 - PORTFOLIO_SECTION_WIDTH - PORTFOLIO_SECTION_MARGIN_R

############# 
# LEFT SIDE #
#############
global_buttons_style = {
    "background-color": 'white1',
    "margin-right": "{0}%",
    "width": "{0}%".format(PORTFOLIO_SECTION_WIDTH),
    "min-width": "50px",
    "height": top_panel_height,
    "float": "left",
    "border-radius": border_radius,
    "overflow-y": "scroll",
    "box-shadow": "6px 6px 12px rgba(0,0,0,0.2)",
}

portfolio_div_style = {
    "background-color": "rgb(246,246,246)",
    "margin-right": "{0}%".format(PORTFOLIO_SECTION_MARGIN_R),
    "width": "{0}%".format(PORTFOLIO_SECTION_WIDTH),
    "min-width": "200px",
    "height": dashboard_height,
    "float": "left",
    "border-radius": border_radius,
    "overflow-y": "scroll",
    "box-shadow": "4px 4px 12px rgba(0,0,0,0.1)",
}

strategy_style = {
    "width": "98%",
    "height": "200px",
    "margin-left": "auto",
    "margin-right": "auto",
    "margin-top": "4px",
    "margin-bottom": "4px",
    "background-color": strategy_bkgd,
    "border": "1px solid rgba(0,0,0,0.6)",
    "border-radius": border_radius,
    "font-family": "Montserrat, sans-serif",
    "font-weight": 100,
    "overflow-y": "scroll",
}

strategy_name_style = {
    "text-align": "center",
    "font-family": "Open-Sans, sans-serif",
    "display": "inline-block",
    "font-size": 30,
    "width": "100%",
    "margin-top": 10,
    "margin-bottom": 10,
}

############## 
# RIGHT SIDE #
##############
fig_div_style = {
    "width": "{0}%".format(BETTING_SECTION_WIDTH),
    "min-width": "800px",
    "height": dashboard_height,
    "float": "left",
    "border-radius": border_radius,
}


dashboard_style = {
    "width": "{0}%".format(BETTING_SECTION_WIDTH),
    "min-width": "800px",
    "height": top_panel_height,
    "float": "left",
    "border-radius": border_radius,
}

title_style = {
    "text-align": "center",
    "background-color": strategy_bkgd,
    "font-family": "Open-Sans, sans-serif",
    "text-align": "center",
    "display": "inline-block",
    "font-size": 25,
    "width": "95%",
    "margin-top": 10,
    "margin-bottom": 10,
}

#########
# EXTRA #
#########
button_style = {
    "width": "10%",
    "margin-left": "2px",
    "margin-right": "2px",
    "height": "100%",
    "float": "left",
    "border-radius": border_radius,
    "font-size": 13,
    "font-family": "Open-Sans, sans-serif",
}

add_tab_button_style = {
    "float": "left",
    "width": "10%",
    "height": "100%",
    "z-index": 9999999,
    "border-radius": border_radius,
}

button_float_right_style = {
    "width": "10%",
    "margin-left": "2px",
    "margin-right": "2px",
    "height": "100%",
    "float": "right",
    "border-radius": border_radius,
    "font-size": "13px",
    "font-family": "Open-Sans, sans-serif",
}

small_button_style = {
    "height": "100%",
    "width": "10%",
    "font-size": 13,
    "margin-left": "2px",
    "margin-right": "2px",
    "float": "left",
    "border-radius": border_radius,
    "font-family": "Open-Sans, sans-serif",
}

button_circular_style = {
    "postion": "relative",
    "height": top_panel_height,
    "width": top_panel_height,
    "font-size": 13,
    "margin-left": "2px",
    "margin-right": "2px",
    # "left": "50%",
    # "transform": "translate(100%, 0)",
    # "float": "left",
    "border-radius": top_panel_height,
    "font-family": "Open-Sans, sans-serif",
}


dropdown_style = {
    "font-size": 14,
    "float": "left",
    "height": top_panel_height,
    "width": "400px",
}

tab_style = {
    "overflow": "hidden",
}

PORTFOLIOS = {
    'port1': {
        'name_0': '1st strat',
        'rebate_pct': 0.26,
        'track': 'track5',
    },
    'port2': {
        'track': 'track5',
    }
}

grey = "rgba(0,0,0,0.6)"
figure_layout = {
    "height": int(dashboard_height[:-2]),
    "paper_bgcolor": white2,
    "plot_bgcolor": white2,
    "xaxis": {
        "tickcolor": grey,
        "tickwidth": 1,
        "title": {"family": "Montserrat, sans-serif", "color": grey},
        "tickfont": {"family": "Montserrat, sans-serif", "color": grey, "size": 15},
    },
    "yaxis": {
        "tickcolor": grey,
        "tickwidth": 1,
        "title": {"family": "Montserrat, sans-serif", "color": grey},
        "tickfont": {"family": "Montserrat, sans-serif", "color": grey, "size": 15},
    },
    "margin": {
        "t": 30,
        "b": 30,
        "r": 0,
        "l": 20
    }
}
