
import dash
import globalvar as gl
from flask_caching import Cache

import dash_core_components as dcc
import dash_html_components as html
import datetime

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import base64
#from layouts_local import *
from layouts import *
import pandas as pd
#import pyarrow as pa
import data_generator
from f04_processor import *




gl._init()

app = dash.Dash(__name__)

server = app.server

app.config.suppress_callback_exceptions = True

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>NXNPERF</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''
'''
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
'''

cnames = ['#00BFFF', '#00008B', '#008B8B', '#B8860B', '#006400', '#BDB76B', '#FF8C00', '#8B0000', '#8FBC8F', '#9400D3']

test_plan = 'baseline'

TIMEOUT = 6000


'''
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
})
'''

cache = Cache(app.server, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': '172.18.0.2',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': '',
    'CACHE_REDIS_PASSWORD': ''
})


@cache.memoize(timeout=TIMEOUT)
def global_store():

    database = data_generator.DataGenerator('baseline')

    dfpl = database.table_extract('Plan')

    dfcs = database.table_extract('Case')

    dfmn = database.table_extract('Main')

    dfnl3 = database.table_extract('Nltrd3')

    key_dict = database.key_dict

    groups2case = dfpl.groupby('GROUP').groups

    groups = sorted(list(groups2case.keys()))

    case_in_group = {}

    for group in groups:

        cases = list(dfpl.loc[list(groups2case[group])]['CASE'])

        case_in_group[group] = cases

    ############## heatmap

    heat_y_axis = sorted(list(dfcs['CASE']))

    heat_x_axis = groups

    heat_z_axis = []

    for i in range(len(heat_y_axis)):

        case_elapsed = []

        for group in groups:

            gc = case_in_group[group]

            if heat_y_axis[i] in gc:

                elapsed = list(dfpl.loc[(dfpl['GROUP'] == group) & (dfpl['CASE'] == heat_y_axis[i])]['ELAPSED'])[0]

                case_elapsed.append(elapsed)

            else:

                case_elapsed.append(None)

        heat_z_axis.append(case_elapsed)

    heatmap_com = [heat_x_axis, heat_y_axis, heat_z_axis]

    case = set()

    for i in range(len(groups)):

        if i == 0:

            case = set(case_in_group[groups[i]])

        else:

            case = case & set(case_in_group[groups[i]])

    latest_baseline_cases = list(case)

    performance_track_latest = {}

    for case_i in latest_baseline_cases:

        elapsed_time = []

        for group in groups:

            elapsed_time .append(list(dfpl.loc[(dfpl['GROUP'] == group) & (dfpl['CASE'] == case_i)]['ELAPSED'])[0])

        performance_track_df = pd.DataFrame(data={'CASE': groups, 'ELAPSED': elapsed_time})

        performance_track_latest[case_i] = performance_track_df

       # performance_track_latest[group] = performance_track_df

    ##################### Performance Curve

    performance_curve = performance_track_latest


    ###################### Latest Case

    latest_cases = list(case_in_group[groups[-1]])

    orderc = ['CASE', 'TEMPLATE']

    for dfc_key in key_dict['Case']:

        if dfc_key != 'CASE' and dfc_key != 'TEMPLATE':

            orderc.append(dfc_key)

    df_latest_case_table = dfcs.copy()[orderc]

    for i in range(len(df_latest_case_table)):

        if df_latest_case_table.loc[i].CASE not in latest_cases:

            df_latest_case_table = df_latest_case_table.drop(i)

    latest_case_table = df_latest_case_table

    #################### Baseline vs Latest

    latest_and_baseline = list(set(case_in_group[groups[-1]]) & set(case_in_group[groups[0]]))

    baseline_elapsed_lb = 0.0

    latest_elapsed_lb = 0.0

    baseline_elapsed_lb_list = []

    latest_elapsed_lb_list = []

    for i in range(len(latest_and_baseline)):

        betime = list(dfpl.loc[(dfpl['GROUP'] == groups[0]) & (dfpl['CASE'] == latest_and_baseline[i])]['ELAPSED'])[0]

        letime = list(dfpl.loc[(dfpl['GROUP'] == groups[-1]) & (dfpl['CASE'] == latest_and_baseline[i])]['ELAPSED'])[0]

        baseline_elapsed_lb = baseline_elapsed_lb + betime

        latest_elapsed_lb = latest_elapsed_lb + letime

        baseline_elapsed_lb_list.append(betime)

        latest_elapsed_lb_list.append(letime)

    lb_vs_elapsed = [round(baseline_elapsed_lb/60, 1), round(latest_elapsed_lb/60, 1)]

    lb_trace_baseline = [latest_and_baseline, baseline_elapsed_lb_list]

    lb_trace_latest = [latest_and_baseline, latest_elapsed_lb_list]

    #################### Prev vs Latest

    latest_and_prev = list(set(case_in_group[groups[-1]]) & set(case_in_group[groups[-2]]))

    prev_elapsed_lp = 0.0

    latest_elapsed_lp = 0.0

    prev_elapsed_lp_list = []

    latest_elapsed_lp_list = []

    regression_case = []

    for i in range(len(latest_and_prev)):

        petime = list(dfpl.loc[(dfpl['GROUP'] == groups[-2]) & (dfpl['CASE'] == latest_and_prev[i])]['ELAPSED'])[0]

        letime = list(dfpl.loc[(dfpl['GROUP'] == groups[-1]) & (dfpl['CASE'] == latest_and_prev[i])]['ELAPSED'])[0]

        if (letime - petime)/petime*100 > 10:

            regression_case.append(latest_and_prev[i])

        prev_elapsed_lp = prev_elapsed_lp + petime

        latest_elapsed_lp = latest_elapsed_lp + letime

        prev_elapsed_lp_list.append(petime)

        latest_elapsed_lp_list.append(letime)

    lp_vs_elapsed = [round(prev_elapsed_lp/60, 1), round(latest_elapsed_lp/60, 1)]

    lp_trace_prev = [latest_and_prev, prev_elapsed_lp_list]

    lp_trace_latest = [latest_and_prev, latest_elapsed_lp_list]

    ########### Regression Case

    df_regression_case_table = dfcs.copy()[orderc]

    for i in range(len(df_regression_case_table)):

        if df_regression_case_table.loc[i].CASE not in regression_case:

            df_regression_case_table = df_regression_case_table.drop(i)

    reg_case_table = df_regression_case_table

    ######### Output to cache file

    #dfpl_json = dfpl.to_json()
    #dfpl_arrow = pa.Table.from_pandas(dfpl)
    #dfcs_json = dfcs.to_json()
    #dfcs_arrow = pa.Table.from_pandas(dfcs)
    #dfmn_json = dfmn.to_json()
    #dfmn_arrow = pa.Table.from_pandas(dfmn)
    #dfnl3_json = dfnl3.to_json()
    #dfnl3_arrow = pa.Table.from_pandas(dfnl3)

    keydict_out = key_dict
    group_out = groups
    performance_curve_out = performance_curve
    #latest_case_table_json = latest_case_table.to_json()
    #latest_case_table_arrow = pa.Table.from_pandas(latest_case_table)
    lb_vs_elapsed_out = lb_vs_elapsed
    lb_trace_baseline_out = lb_trace_baseline
    lb_trace_latest_out = lb_trace_latest

    lp_vs_elapsed_out = lp_vs_elapsed
    lp_trace_prev_out = lp_trace_prev
    lp_trace_latest_out = lp_trace_latest

    #reg_case_table_out = reg_case_table.to_json()
    #reg_case_table_out = pa.Table.from_pandas(reg_case_table)

    out = {'dfpl': dfpl, 'dfcs': dfcs, 'dfmn': dfmn, 'dfnl3': dfnl3, 'keydict': key_dict,
           'groups': group_out, 'performance_curve': performance_curve_out, 'latest_case_table': latest_case_table,
           'lb_vs_elapsed': lb_vs_elapsed_out, 'lb_trace_baseline': lb_trace_baseline_out,
           'lb_trace_latest': lb_trace_latest_out, 'lp_vs_elapsed': lp_vs_elapsed_out,
           'lp_trace_prev': lp_trace_prev_out, 'lp_trace_latest': lp_trace_latest_out,
           'reg_case_table': reg_case_table, 'case_in_group': groups2case, 'case_group_matrix':case_in_group,
           'heatmap': heatmap_com}

    return out


@app.callback(Output('signal', 'children'), [Input('case_open', 'value')])
def compute_value(value):
    # compute value and send a signal when done
    out = global_store()

    return value


def Hex_to_RGB(hex):

    r = int(hex[1:3], 16)
    g = int(hex[3:5], 16)
    b = int(hex[5:7], 16)
    rgb = str(r) + ',' + str(g) + ',' + str(b)
    return rgb


def generate_table(dataframe, max_rows=1000):

    return html.Table(
        # Header
        [html.Thead(html.Tr([html.Th(col) for col in dataframe.columns]))] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


def layout_update():

    main_container = container_generator()

    return html.Div([
        html.Div(id='signal', style={'display': 'none'}),
        html.Div(main_container)
    ])


app.layout = layout_update


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    [Output("case_badges", "children"),
     Output("case_modal", "children"),
     Output("case_number", "children")],
    [Input("signal", "value")],
)
def update_case_content(value):

    global_var = global_store()

    badge_list = global_var['keydict']['Case']

    cmd = ''

    index = 0

    bcnames = ['primary', 'success', 'danger', 'warning', 'info']

    for badge in badge_list:

        if badge != 'CASE' and badge != 'TEMPLATE':

            if index == 0:

                cmd = "dbc.Badge('" + badge + "', color='" + bcnames[0] + "', pill=True, className='mr-1 mt-2 mb-2', " \
                                                                          "style={'font-size':'0.7rem'})"

            elif index <= 3:

                ind = (index // len(bcnames))

                kp = index - len(bcnames) * ind

                cmd = cmd + ',' + "dbc.Badge('" + badge + "', color='" + bcnames[kp] + "', pill=True, " \
                                                          "className='mr-1 mt-2 mb-2', style={'font-size':'0.7rem'})"

            index = index + 1

    badge_cmd = 'html.Span([' + cmd + '])'

    case_badges = eval(badge_cmd)

    #dfc = pd.read_json(global_var['latest_case_table'])

    #dfc = global_var['latest_case_table'].to_pandas()

    dfc = global_var['latest_case_table']

    case_number = str(len(dfc)) + " Cases"

    table_case = dbc.Table(
        generate_table(dfc),
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        className='table-success'
    )

    case_modal = html.Div(
        [
            dbc.Button("View Detail", id="case_open", color='success', outline=True, block=True, className='btn-sm'),
            dbc.Modal(
                [
                    dbc.ModalHeader("Testing Cases"),
                    dbc.ModalBody(table_case, style={'margin': 'auto'}),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="case_close", className="ml-auto")
                    ),
                ],
                id="case_modal",
                size='lg',
                scrollable=True,
                centered=True
            ),
        ]
    )

    return case_badges, case_modal, case_number


@app.callback(
    [Output("latest_group_lb", "children"),
     Output("latest_elapsed_lb", "children"),
     Output("baseline_group_lb", "children"),
     Output("baseline_elapsed_lb", "children"),
     Output("lb_process", "children"),
     Output("otb_modal", "children"),
     ],
    [Input("signal", "value")],
)
def update_time_content(value):

    global_var = global_store()

    groups = global_var['groups']

    latest_group = groups[-1]

    baseline_group = groups[0]

    lb_vs_collapsed = global_var['lb_vs_elapsed']

    latest_elapsed_lb = lb_vs_collapsed[1]

    baseline_elapsed_lb = lb_vs_collapsed[0]

    perf_increase_lb = round((baseline_elapsed_lb - latest_elapsed_lb) / baseline_elapsed_lb * 100, 1)

    if perf_increase_lb < 0:

        process_bar_cmd_lb = "dbc.Progress([dbc.Progress(children='" + str(100) + "%', value=" \
                             + str(100-abs(perf_increase_lb)) + ", color='warning', bar=True)," \
                              + "dbc.Progress(children='" + str(abs(perf_increase_lb)) + "%', value=" + str(perf_increase_lb) \
                              + ", color='danger', bar=True)], multi=True, style={'font-size':'0.8rem', 'height': '35px'}),"

    else:

        process_bar_cmd_lb = "dbc.Progress([dbc.Progress(children='" + str(100 - perf_increase_lb) + "%', value=" \
                             + str(100-perf_increase_lb) + ", color='success', bar=True)," \
                              + "dbc.Progress(children='" + str(perf_increase_lb) + "%', value=" + str(perf_increase_lb) \
                              + ", color='warning', bar=True)], multi=True, style={'font-size':'0.8rem', 'height': '35px'}),"

    lb_process = eval(process_bar_cmd_lb)

    lb_trace_baseline = global_var['lb_trace_baseline']
    lb_trace_latest = global_var['lb_trace_latest']

    trace_latest_lb = go.Bar(x=lb_trace_latest[0], y=lb_trace_latest[1], name=latest_group)
    trace_baseline_lb = go.Bar(x=lb_trace_baseline[0], y=lb_trace_baseline[1], name=baseline_group)

    trace_lb = [trace_baseline_lb, trace_latest_lb]

    otb_graph = dcc.Graph(
        id='otb_graph',
        figure={
            "data": trace_lb,
            "layout": {
                "xaxis": {"automargin": True},
                "yaxis": {
                    "automargin": True,
                },
                "height": '400',
                "margin": {"t": 10, "l": 10, "r": 10},
                "legend": dict(x=0.0, y=1.0),
            },
        },
    )

    otb_modal = html.Div(
        [
            dbc.Button("View Detail", id="otb_open", color='primary', outline=True, block=True, className='btn-sm'),
            dbc.Modal(
                [
                    dbc.ModalHeader("Overall Time Compared with Baseline"),
                    dbc.ModalBody(otb_graph, style={'margin': 'auto'}),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="otb_close", className="ml-auto")
                    ),
                ],
                id="otb_modal",
                size='lg',
                scrollable=True,
                centered=True
            ),
        ]
    )

    return latest_group, latest_elapsed_lb, baseline_group, baseline_elapsed_lb, lb_process, otb_modal


@app.callback(
    [Output("latest_group_lp", "children"),
     Output("latest_elapsed_lp", "children"),
     Output("prev_group_lp", "children"),
     Output("prev_elapsed_lp", "children"),
     Output("lp_process", "children"),
     Output("otp_modal", "children"),
     ],
    [Input("signal", "value")],
)
def update_time_content1(value):

    global_var = global_store()

    groups = global_var['groups']

    latest_group = groups[-1]

    prev_group = groups[-2]

    lp_vs_collapsed = global_var['lp_vs_elapsed']

    latest_elapsed_lp = lp_vs_collapsed[1]

    prev_elapsed_lp = lp_vs_collapsed[0]

    perf_increase_lp = round((prev_elapsed_lp - latest_elapsed_lp) / prev_elapsed_lp * 100, 1)

    if perf_increase_lp < 0:

        process_bar_cmd_lp = "dbc.Progress([dbc.Progress(children='" + str(100) + "%', value=" \
                             + str(100 - abs(perf_increase_lp)) + ", color='warning', bar=True)," \
                             + "dbc.Progress(children='" + str(abs(perf_increase_lp)) + "%', value=" + \
                             str(perf_increase_lp) \
                             + ", color='danger', bar=True)], multi=True, style={'font-size':'0.8rem', 'height': '35px'}),"

    else:

        process_bar_cmd_lp = "dbc.Progress([dbc.Progress(children='" + str(100 - perf_increase_lp) + "%', value=" \
                             + str(100 - perf_increase_lp) + ", color='success', bar=True)," \
                             + "dbc.Progress(children='" + str(perf_increase_lp) + "%', value=" + str(perf_increase_lp) \
                             + ", color='warning', bar=True)], multi=True, style={'font-size':'0.8rem', 'height': '35px'}),"

    lp_process = eval(process_bar_cmd_lp)

    lp_trace_prev = global_var['lp_trace_prev']
    lp_trace_latest = global_var['lp_trace_latest']

    trace_latest_lp = go.Bar(x=lp_trace_latest[0], y=lp_trace_latest[1], name=latest_group)
    trace_prev_lp = go.Bar(x=lp_trace_prev[0], y=lp_trace_prev[1], name=prev_group)

    trace_lp = [trace_prev_lp, trace_latest_lp]

    otp_graph = dcc.Graph(
        id='otp_graph',
        figure={
            "data": trace_lp,
            "layout": {
                "xaxis": {"automargin": True},
                "yaxis": {
                    "automargin": True,
                },
                "height": '400',
                "margin": {"t": 10, "l": 10, "r": 10},
                "legend": dict(x=0.0, y=1.0),
            },
        },
    )

    otp_modal = html.Div(
        [
            dbc.Button("View Detail", id="otp_open", color='primary', outline=True, block=True, className='btn-sm'),
            dbc.Modal(
                [
                    dbc.ModalHeader("Overall Time Compared with Baseline"),
                    dbc.ModalBody(otp_graph, style={'margin': 'auto'}),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="otp_close", className="ml-auto")
                    ),
                ],
                id="otp_modal",
                size='lg',
                scrollable=True,
                centered=True
            ),
        ]
    )

    return latest_group, latest_elapsed_lp, prev_group, prev_elapsed_lp, lp_process, otp_modal


@app.callback(
    [Output("reg_case_number", "children"),
     Output("reg_progress", "children"),
     Output("reg_modal", "children")],
    [Input("signal", "value")],
)
def update_time_content2(value):

    global_var = global_store()

    #reg_case_table = pd.read_json(global_var['reg_case_table'])

    #reg_case_table = global_var['reg_case_table'].to_pandas()

    reg_case_table = global_var['reg_case_table']

    #dfc = pd.read_json(global_var['latest_case_table'])

    #dfc = global_var['latest_case_table'].to_pandas()

    dfc = global_var['latest_case_table']

    reg_lp_case = reg_case_table

    reg_case_number = str(len(reg_case_table)) + ' Cases'

    latest_case_number = len(dfc)

    reg_progress = dbc.Progress(
        [
            dbc.Progress(children=str(latest_case_number - len(reg_lp_case)) + ' Cases',
                         value=(latest_case_number - len(reg_lp_case)) / latest_case_number * 100,
                         color='success', bar=True),

            dbc.Progress(children=str(len(reg_lp_case)),
                         value=(len(reg_lp_case)) / latest_case_number * 100,
                         color='danger', bar=True),
        ],
        multi=True,
        style={'font-size': '0.8rem', 'height': '30px'},
        className='mt-3'
    )

    if len(reg_lp_case) == 0:

        Reg_Flag = True

        reg_graph_lp = html.Div([])

        table_reg_case_p = html.Div([])

    else:

        Reg_Flag = False

        lp_trace_prev = global_var['lp_trace_prev']

        lp_trace_latest = global_var['lp_trace_latest']

        groups = global_var['groups']

        reg_prev_elapsed_list = []

        reg_latest_elapsed_list = []

        reg_case_list = list(reg_case_table.loc['CASE'])

        for case in reg_case_list:

            i = lp_trace_latest[0].index(case)
            j = lp_trace_prev[0].index(case)

            reg_latest_elapsed_list.append(lp_trace_latest[i])
            reg_prev_elapsed_list.append(lp_trace_prev[j])

        reg_trace_prev = go.Bar(x=reg_case_list, y=reg_prev_elapsed_list, name=groups[-2])
        reg_trace_lp_latest = go.Bar(x=reg_case_list, y=reg_latest_elapsed_list, name=groups[-1])
        reg_trace_lp = [reg_trace_prev, reg_trace_lp_latest]

        reg_graph_lp = dcc.Graph(
            id='reg_graph_lp',
            figure={
                "data": reg_trace_lp,
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                    },
                    "height": 500,
                    "margin": {"t": 10, "l": 10, "r": 10},
                    "legend": dict(x=0.0, y=1.0),
                },
            },
        )

        table_reg_case_p = dbc.Table(
            generate_table(reg_case_table),
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
            className='table-danger'
        )

    reg_modal = html.Div(
        [
            dbc.Button("View Detail", id="reg_open", color='danger', outline=True, block=True, className='btn-sm', disabled=Reg_Flag),
            dbc.Modal(
                [
                    dbc.ModalHeader("Regression Cases compared with Previous Group"),
                    dbc.ModalBody(
                        [
                            dbc.Jumbotron(
                                [
                                    dbc.Row(
                                        [
                                            html.H6('Elapsed time increase more than 5%')
                                        ],
                                        justify='start',
                                        align='center',
                                        className='mb-2 ml-2'
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(table_reg_case_p, width=12),
                                        ],
                                        justify='center',
                                        align='center',
                                        className='mb-2'
                                    ),
                                ],
                            ),
                            dbc.Jumbotron(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(reg_graph_lp, width=12),
                                        ],
                                        justify='center',
                                        align='center',
                                        className='mb-2'
                                    ),
                                ]
                            ),

                        ],
                        style={'margin': 'auto'}),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="reg_close", className="ml-auto")
                    ),
                ],
                id="reg_modal",
                size='lg',
                scrollable=True,
                centered=True
            ),
        ]
    )

    return reg_case_number, reg_progress, reg_modal


@app.callback(
    [Output("history_table", "children"),
     Output("showing_graph", "children")],
    [Input("signal", "value")],
)
def update_case_detail_container(value):

    global_var = global_store()

    #dfpl = pd.read_json(global_var['dfpl'])

    #dfpl = global_var['dfpl'].to_pandas()

    dfpl = global_var['dfpl']

    df = dfpl.sort_values(by="GROUP", ascending=False)

    df['index'] = range(1, len(df) + 1)

    df.drop('RESULT', axis=1)

    order = ['DATE', 'CASE', 'GROUP', 'ELAPSED']

    df = df[order]

    PAGE_SIZE = 15

    table1 = dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i} for i in df.columns
        ],
        data=df.to_dict('records'),
        editable=False,
        filter_action="native",
        sort_action="native",
        sort_mode="single",
        #row_selectable="multi",
        row_deletable=False,
        #selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=PAGE_SIZE,
        page_count=math.ceil(df.shape[0]/PAGE_SIZE),

        style_cell={'textAlign': 'center', 'padding': '2px', 'font-size': '0.7rem', 'fontWeight': 'bold'},
        #style_as_list_view=True,

        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['CASE', 'DATE']
        ],

        style_data_conditional=[
            {'if': {'column_id': 'DATE'},
             'width': '6.25rem'},
            {'if': {'column_id': 'CASE'},
             'width': '6.25rem'},
            {'if': {'column_id': 'GROUP'},
             'width': '4.67rem'},
            {'if': {'column_id': 'ELAPSED'},
             'width': '4.25rem'},
        ],
        style_header={
            'backgroundColor': 'rgb(210, 230, 230)',
            'fontWeight': 'bold'
        }
    )

    spinners = html.Div(
        [
            dbc.Spinner(color="primary", type="grow"),
            dbc.Spinner(color="secondary", type="grow"),
            dbc.Spinner(color="success", type="grow"),
            dbc.Spinner(color="warning", type="grow"),
            dbc.Spinner(color="danger", type="grow"),
            dbc.Spinner(color="info", type="grow"),
            dbc.Spinner(color="dark", type="grow"),
        ]
    )

    showing_graph = html.Div(id='vision_box', children=spinners, style={'height':'50rem'})

    return table1, showing_graph


@app.callback(
    [Output("group_range", "children"),
     Output("group-multi-dynamic-dropdown", "options"),
     Output("trend_group_start", "options"),
     Output("trend_group_end", "options")],
    [Input("signal", "value")],
)
def update_search_area(value):

    global_var = global_store()

    groups = global_var['groups']

    gl.set_value('total_groups', groups)

    gopts = []

    for i in groups:

        gopts.append({"label":  i, "value": i})

    if len(groups) <= 6:

        range_max = len(groups)-1

        range_labels = list(range(len(groups)))

    else:

        gn = gl.get_value('range_group')

        range_labels = []

        for i in range(gn+1):

            new_index = math.ceil(0 + len(groups) / gn * i)

            if new_index > len(groups)-1:

                range_labels.append(len(groups)-1)

            else:

                range_labels.append(new_index)

        range_max = gn

    range_slider = dcc.RangeSlider(
        count=1,
        min=0,
        max=range_max,
        value=[0, range_max],
        marks={i: groups[range_labels[i]] for i in range(len(range_labels))},
        id='group_range_slider'
    )

    return range_slider, gopts, gopts, gopts


def create_time_series(dff):

    global_var = global_store()

    performance_curve = global_var['performance_curve'].copy()

    colors = []

    for i in range(len(dff)):

        index = (i // len(cnames))

        kp = i - len(cnames) * index

        colors.append(cnames[kp])

    fig = go.Figure()

    index = 0

    for i in range(len(dff)):

        case = dff.loc[i, 'CASE']

        if case in performance_curve.keys():

            elapsed = performance_curve[case]

            x_list = list(elapsed['CASE'])

            y_list = list(elapsed['ELAPSED'])

            fig.add_trace(
                go.Scatter(
                    x=x_list,
                    y=y_list,
                    name=case,
                    mode='lines+markers',
                    line=dict(color='rgba(' + Hex_to_RGB(colors[index]) + ', 0.5)', width=4),
                    marker=dict(color=colors[index], size=10, opacity=0.5,
                                line=dict(color='MediumPurple', width=2))))

            index = index + 1

            performance_curve.pop(case)

    fig.update_layout(template='seaborn',
                        height=600,
                      margin=dict(
                          l=0,
                          r=0,
                          b=10,
                          t=10,
                          pad=0
                      ),
                      font=dict(
                        family="Courier New, monospace",
                        size=10,
                        color="black"
                      )
                      )

    fig.update_layout(xaxis_type='category')

    fig.update_layout(showlegend=True)
    fig.update_layout(legend_orientation="h")
    fig.update_layout(
        legend=dict(
            font=dict(
                family="Courier New, monospace",
                size=8,
                color="black"
            ),
        )
    )
    #fig.update_layout(legend={'itemsizing': 'constant'})
    #fig.update_layout(legend=dict(x=-0.1, y=-0.1))

    return dcc.Graph(id='histroy_elapsed', figure=fig, style={'height':'37rem'})


@app.callback(
    Output('vision_box', "children"),
    [Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "derived_virtual_selected_rows")])
def update_graphs(rows, derived_virtual_selected_rows):

    if derived_virtual_selected_rows is None:

        derived_virtual_selected_rows = []

    try:

        dff = df if rows is None else pd.DataFrame(rows)

    except:

        dff=[]

    return create_time_series(dff)

@app.callback(
    Output("case_modal", "is_open"),
    [Input("case_open", "n_clicks"), Input("case_close", "n_clicks")],
    [State("case_modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("otb_modal", "is_open"),
    [Input("otb_open", "n_clicks"), Input("otb_close", "n_clicks")],
    [State("otb_modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("otp_modal", "is_open"),
    [Input("otp_open", "n_clicks"), Input("otp_close", "n_clicks")],
    [State("otp_modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("reg_modal", "is_open"),
    [Input("reg_open", "n_clicks"), Input("reg_close", "n_clicks")],
    [State("reg_modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    [Output("case-single-dynamic-dropdown", "options"),
     Output("case-single-dynamic-dropdown", "disabled"),
     Output("case-single-dynamic-dropdown", "value")],
    [Input("group-multi-dynamic-dropdown", "value")],
)
def update_single_options(group_value):

    global_var = global_store()

    #dfcl = pd.read_json(global_var['dfpl'])

    #dfcl = global_var['dfpl'].to_pandas()

    dfcl = global_var['dfpl']

    group_key_list = global_var['case_in_group']

    group_out = []

    flag = True

    if group_value is not None:

        if len(group_value) > 0:

            item_target = set()

            index = 0

            for key in group_value:

                if index == 0:

                    item_target = set(dfcl.loc[list(group_key_list[key]), 'CASE'])

                else:

                    item_target = item_target & set(dfcl.loc[list(group_key_list[key]), 'CASE'])

                index = index + 1

            options = []

            for case in list(item_target):

                options.append({"label": case, "value": case})

            group_out = options

            flag = False

    return group_out, flag, "Input case name ..."


def create_compare_figure(group_value, case_value, module_print_threshold):

    global_var = global_store()

    #dfpl = pd.read_json(global_var['dfpl'])

    #dfmn = pd.read_json(global_var['dfmn'])

    #dfpl = global_var['dfpl'].to_pandas()

    #dfmn = global_var['dfmn'].to_pandas()

    dfpl = global_var['dfpl']

    dfmn = global_var['dfmn']

    fig = go.Figure()

    default = html.Div(dbc.Card(
            [
                html.Div(
                    [
                        dbc.CardImg(src="./assets/img/perf_compare_main7.png", top=True, style={'width': '100%',
                                                                                                   'height': '100%'}),
                    ],
                ),
                dbc.CardBody(
                    [
                        html.H6("Main Module Elapsed Time", className="card-title", style={'font-size': '80%'}),
                        html.P(
                            "The elapsed time of main modules will be ploted here.",
                            className="card-text",
                            style={'font-size': '0.5rem'}
                        ),
                    ]
                )
            ],
            color='success',
            inverse=True
        ),
            id="compare_graph",
        )

    if group_value is not None:

        chk_group1 = (len(group_value) > 0)

    else:

        chk_group1 = False

    if case_value is not None:

        chk_case1 = (case_value != 'Input case name ...')

    else:

        chk_case1 = False

    if (chk_group1 is True) and (chk_case1 is True):

        for group in sorted(group_value):

            result_key = list(dfpl.loc[(dfpl['CASE'] == case_value) & (dfpl['GROUP'] == group)]['RESULT'])[0]

            elapsed = list(dfpl.loc[(dfpl['CASE'] == case_value) & (dfpl['GROUP'] == group)]['ELAPSED'])[0]

            main = dfmn.copy().loc[dfmn['MAIN'] == result_key]

            main = main.drop(['MAIN'], axis=1)

            x_list = list(main.columns.values.tolist())

            y_list = list(main.iloc[0])

            x_list.append('ELAPSED')

            y_list.append(elapsed)

            list_tract = dict(zip(x_list, y_list))

            aps = sorted(list_tract.items(), key=lambda a: a[1], reverse=True)

            x1 = []

            y1 = []

            for key in aps:

                if key[1] >= module_print_threshold:

                    x1.append(key[0])

                    y1.append(key[1])

            fig.add_trace(go.Bar(x=x1,
                                 y=y1,
                                 name=group,
                                 #marker_color='rgb(55, 83, 109)'
                                 ))

    elif (chk_group1 is False) or (chk_case1 is False):

        return default

    fig.update_layout(
        xaxis_tickfont_size=8,
        yaxis=dict(
            titlefont_size=16,
            tickfont_size=8,
        ),

        legend=dict(
            x=0.7,
            y=0.92,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
            font=dict(
                family="Courier New, monospace",
                size=12,
                color="black"
            ),
        ),
        barmode='group',
        bargap=0.15,  # gap between bars of adjacent location coordinates.
        bargroupgap=0.1  # gap between bars of the same location coordinate.
    )

    fig.update_layout(
        title={
            'text': "Main Modules Elapsed Time",
            'y': 0.95,
            'x': 0.95,
            'xanchor': 'right',
            'yanchor': 'top',
        },
        titlefont={
            "size": 12,
            'color': 'black'
        },
    )

    fig.update_layout(template='seaborn',
                        height=400,
                      margin=dict(
                          l=0,
                          r=0,
                          b=0,
                          t=0,
                          pad=0
                      ),
                      )

    return dcc.Graph(id='comp_figure', figure=fig)


def create_compare_figure1(group_value, case_value, module_print_threshold):

    global_var = global_store()

    #dfpl = pd.read_json(global_var['dfpl'])

    #dfmn = pd.read_json(global_var['dfnl3'])

    #dfpl = global_var['dfpl'].to_pandas()

    #dfmn = global_var['dfnl3'].to_pandas()

    dfpl = global_var['dfpl']

    dfmn = global_var['dfnl3']

    fig = go.Figure()

    default = html.Div(dbc.Card(
        [
            html.Div(
                [
                    dbc.CardImg(src="./assets/img/perf_compare_main7.png", top=True, style={'width': '100%',
                                                                                               'height': '100%'}),
                ],
            ),
            dbc.CardBody(
                [
                    html.H6("Main Module Elapsed Time", className="card-title", style={'font-size': '80%'}),
                    html.P(
                        "The elapsed time of main modules will be ploted here.",
                        className="card-text",
                        style={'font-size': '0.5rem'}
                    ),
                ]
            )
        ],
        color='success',
        inverse=True
    ),
        id="compare_graph",
    )

    if group_value is not None:

        chk_group1 = (len(group_value) > 0)

    else:

        chk_group1 = False

    if case_value is not None:

        chk_case1 = (case_value != 'Input case name ...')

    else:

        chk_case1 = False

    if (chk_group1 is True) and (chk_case1 is True):

        for group in sorted(group_value):

            result_key = list(dfpl.loc[(dfpl['CASE'] == case_value) & (dfpl['GROUP'] == group)]['RESULT'])[0]

            main = dfmn.copy().loc[dfmn['NLTRD3'] == result_key]

            main = main.drop(['NLTRD3'], axis=1)

            x_list = list(main.columns.values.tolist())

            y_list = list(main.iloc[0])

            list_tract = dict(zip(x_list, y_list))

            aps = sorted(list_tract.items(), key=lambda a: a[1], reverse=True)

            x1 = []

            y1 = []

            for key in aps:

                if key[1] >= module_print_threshold:

                    x1.append(key[0])

                    y1.append(key[1])

            fig.add_trace(go.Bar(x=x1,
                                 y=y1,
                                 name=group,
                                 #marker_color='rgb(55, 83, 109)'
                                 ))

    elif (chk_group1 is False) or (chk_case1 is False):

        return default

    fig.update_layout(
        xaxis_tickfont_size=8,
        yaxis=dict(
            titlefont_size=16,
            tickfont_size=8,
        ),

        legend=dict(
            x=0.7,
            y=0.92,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
            font=dict(
                family="Courier New, monospace",
                size=12,
                color="black"
            ),
        ),
        barmode='group',
        bargap=0.15,  # gap between bars of adjacent location coordinates.
        bargroupgap=0.1  # gap between bars of the same location coordinate.
    )

    fig.update_layout(
        title={
            'text': "NLTRD3 Submodules Elapsed Time",
            'y': 0.95,
            'x': 0.95,
            'xanchor': 'right',
            'yanchor': 'top',
        },
        titlefont={
            "size": 12,
            'color': 'black'
        },
    )

    fig.update_layout(template='seaborn',
                        height=400,
                      margin=dict(
                          l=0,
                          r=0,
                          b=0,
                          t=0,
                          pad=0
                      ),
                      )

    return dcc.Graph(id='comp_figure1', figure=fig)


def create_compare_table(group_value, case_value):

    global_var = global_store()

    #dfpl = pd.read_json(global_var['dfpl'])

    #dfmn = pd.read_json(global_var['dfmn'])

    #dfnl3 = pd.read_json(global_var['dfnl3'])

    #dfpl = global_var['dfpl'].to_pandas()

    #dfmn = global_var['dfmn'].to_pandas()

    #dfnl3 = global_var['dfpl'].to_pandas()

    dfpl = global_var['dfpl']

    dfmn = global_var['dfmn']

    dfnl3 = global_var['dfnl3']

    index = 0

    if group_value is not None:

        chk_group1 = (len(group_value) > 0)

    else:

        chk_group1 = False

    if case_value is not None:

        chk_case1 = (case_value != 'Input case name ...')

    else:

        chk_case1 = False

    if (chk_group1 is True) and (chk_case1 is True):

        for group in sorted(group_value):

            result_key = list(dfpl.loc[(dfpl['CASE'] == case_value) & (dfpl['GROUP'] == group)]['RESULT'])[0]

            nltrd3 = dfnl3.copy().loc[dfnl3['NLTRD3'] == result_key]

            nltrd3 = nltrd3.drop(['NLTRD3'], axis=1)

            nltrd3.insert(0, 'GROUP', group)

            main = dfmn.copy().loc[dfmn['MAIN'] == result_key]

            main = main.drop(['MAIN'], axis=1)

            main.insert(0, 'GROUP', group)

            if index == 0:

                df_nltrd3 = nltrd3

                df_main = main

            else:

                df_nltrd3 = df_nltrd3.append(nltrd3)

                df_main = df_main.append(main)

            index = index + 1

    elif (chk_group1 is False) or (chk_case1 is False):

        return [], []

    for col in df_main.columns:

        if col != 'GROUP':

            etime = sum(list(df_main[col]))

            if etime == 0.0:

                df_main = df_main.drop(col, axis=1)

    for col in df_nltrd3.columns:

        if col != 'GROUP':

            etime = sum(list(df_nltrd3[col]))

            if etime == 0.0:

                df_nltrd3 = df_nltrd3.drop(col, axis=1)

    table_main = dash_table.DataTable(
        id='datatable-interactivity-main',
        columns=[
            {"name": i, "id": i} for i in df_main.columns
        ],
        data=df_main.to_dict('records'),
        editable=False,
        sort_action="native",
        sort_mode="single",
        # row_selectable="multi",
        row_deletable=False,
        # selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=5,
        page_count=math.ceil(df_main.shape[0] / 5),

        style_cell={'textAlign': 'center', 'padding': '2px', 'font-size': '0.7rem', 'fontWeight': 'bold'},
        # style_as_list_view=True,

        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['CASE', 'DATE']
        ],


        style_header={
            'backgroundColor': 'rgb(210, 230, 230)',
            'fontWeight': 'bold'
        }
    )

    table_nltrd3 = dash_table.DataTable(
        id='datatable-interactivity-main',
        columns=[
            {"name": i, "id": i} for i in df_nltrd3.columns
        ],
        data=df_nltrd3.to_dict('records'),
        editable=False,
        sort_action="native",
        sort_mode="single",
        # row_selectable="multi",
        row_deletable=False,
        # selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=5,
        page_count=math.ceil(df_nltrd3.shape[0] / 5),

        style_cell={'textAlign': 'center', 'padding': '2px', 'font-size': '0.7rem', 'fontWeight': 'bold'},
        # style_as_list_view=True,

        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['CASE', 'DATE']
        ],


        style_header={
            'backgroundColor': 'rgb(210, 230, 230)',
            'fontWeight': 'bold'
        }
    )

    return table_main, table_nltrd3


@app.callback(
    [Output('compare_graph', 'children'),
     Output('compare_graph1', 'children'),
     Output('compare_table', 'children'),
     Output('compare_table1', 'children')],
    [Input('search_start', 'n_clicks')],
    [State('group-multi-dynamic-dropdown', 'value'),
     State('case-single-dynamic-dropdown', 'value'),
     State('switches-inline-input', 'value')])
def update_output(n_clicks, group_value, case_value, switch_value):

    if not n_clicks:

        raise PreventUpdate

    if 1 in switch_value:

        module_print_threshold = 0.0

    else:

        module_print_threshold = 10.0

    if 2 in switch_value:

        table_main, table_nltrd3 = create_compare_table(group_value, case_value)

    else:

        table_main = []

        table_nltrd3 = []

    return create_compare_figure(group_value, case_value, module_print_threshold),\
           create_compare_figure1(group_value, case_value, module_print_threshold),\
           table_main, table_nltrd3


@app.callback(
    [Output("trend_group_start", "value"),
     Output("trend_group_end", "value")],
    [Input("group_range_slider", "value")],
)
def add_range_group(range_group):

    groups = global_store()['groups']

    if len(groups) <= 6:

        range_max = len(groups) - 1

        range_labels = list(range(len(groups)))

    else:

        gn = gl.get_value('range_group')

        range_labels = []

        for i in range(gn + 1):

            new_index = math.ceil(0 + len(groups) / gn * i)

            if new_index > len(groups) - 1:

                range_labels.append(len(groups) - 1)

            else:

                range_labels.append(new_index)

    return groups[range_labels[range_group[0]]], groups[range_labels[range_group[1]]]


def create_track_plot(start, end, flag):

    global_var = global_store()

    dfpl = global_var['dfpl']

    groups = global_var['groups']

    case_group_matrix = global_var['case_group_matrix']

    start_index = groups.index(start)

    end_index = groups.index(end)

    case = set()

    x_list = []

    y_list = []

    if flag == 1:

        for i in range(start_index, end_index + 1):

            if i == start_index:

                case = set(case_group_matrix[groups[i]])

            else:

                case = case & set(case_group_matrix[groups[i]])

            x_list.append(groups[i])

        latest_baseline_cases = list(case)

        for i in range(start_index, end_index + 1):

            elapsed_time = []

            for case_i in latest_baseline_cases:

                elapsed_time.append(list(dfpl.loc[(dfpl['GROUP'] == groups[i]) & (dfpl['CASE'] == case_i)]['ELAPSED'])[0])

            y_list.append(round(sum(elapsed_time)/60, 1))

    else:

        case = set(case_group_matrix[groups[start_index]]) & set(case_group_matrix[groups[end_index]])

        x_list = [groups[start_index], groups[end_index]]

        elapsed_time_start = []

        elapsed_time_end = []

        for case_i in case:

            elapsed_time_start.append(list(dfpl.loc[(dfpl['GROUP'] == groups[start_index]) & (dfpl['CASE'] == case_i)]['ELAPSED'])[0])

            elapsed_time_end.append(list(dfpl.loc[(dfpl['GROUP'] == groups[end_index]) & (dfpl['CASE'] == case_i)]['ELAPSED'])[0])

        y_list = [round(sum(elapsed_time_start)/60, 1), round(sum(elapsed_time_end)/60, 1)]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x_list,
            y=y_list,
            name='Total Elapsed Time (Mins)',
            mode='lines+markers',
            line=dict(color='rgba(' + Hex_to_RGB('#B8860B') + ', 0.5)', width=7),
            marker=dict(color='#00008B', size=10, opacity=0.5,
                        line=dict(color='MediumPurple', width=5))))

    fig.update_layout(template='seaborn',
                        height=500,
                      margin=dict(
                          l=0,
                          r=0,
                          b=10,
                          t=10,
                          pad=0
                      ),
                      legend=dict(
                          x=0.62,
                          y=0.97,
                          bgcolor='rgba(255, 255, 255, 0)',
                          bordercolor='rgba(255, 255, 255, 0)',
                          font=dict(
                              family="Courier New, monospace",
                              size=12,
                              color="black"
                          ),
                      ),
                      font=dict(
                        family="Courier New, monospace",
                        size=10,
                        color="black"
                      )
                      )

    fig.update_layout(xaxis_type='category')

    fig.update_layout(showlegend=True)
    fig.update_layout(legend_orientation="h")
    fig.update_layout(
        legend=dict(
            font=dict(
                family="Courier New, monospace",
                size=10,
                color="black"
            ),
        )
    )

    return dcc.Graph(id='track_plot_graph', figure=fig, style={'margin-left': '-1rem', 'height':'30rem'})


@app.callback(
    Output('track_plot', "children"),
    [Input('search_track', "n_clicks")],
    [State('switches-inline-input-track', "value"),
     State('trend_group_start', "value"),
     State('trend_group_end', "value")])
def update_graphs(n_clicks, switch_value, value1, value2):

    if not n_clicks:

        global_var = global_store()

        start = global_var['groups'][0]

        end = global_var['groups'][-1]

    else:

        rangel = sorted([value1, value2])

        start = rangel[0]

        end = rangel[1]

    if switch_value is None:

        flag = 1

    else:

        if len(switch_value) == 0:

            flag = 1

        else:

            flag = 0

    return create_track_plot(start, end, flag)


@app.callback(
    Output("case_heatmap", "children"),
    [Input("signal", "value")],
)
def update_matrix_area(value):

    global_var = global_store()

    heat = global_var['heatmap']

    fig = go.Figure(
        data=go.Heatmap(
        z=heat[2],
        x=heat[0],
        y=heat[1],
        hoverongaps=False,
        colorscale='Tealgrn',
        zmin = 1000,
        zmid = 7000,
        zmax = 10000,
        xgap = 2
        ))

    fig.update_layout(
        xaxis_type='category',
        xaxis_tickfont_size=8,
        yaxis=dict(
            titlefont_size=16,
            tickfont_size=8,
        ),
    )

    fig.update_layout(template='seaborn',
                        height=760,
                      margin=dict(
                          l=0,
                          r=0,
                          b=0,
                          t=0,
                          pad=0
                      ),
                      )

    #fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    return dcc.Graph(id='heatmap_graph', figure=fig, style={'height':'48.10rem'})


def external_create_compare_figure(filename, x_list_set, y_list_set):

    fig = go.Figure()

    for i in range(len(x_list_set)):

        fig.add_trace(go.Bar(x=x_list_set[i],
                             y=y_list_set[i],
                             name=filename[i],
                             #marker_color='rgb(55, 83, 109)'
                             ))

    fig.update_layout(
        xaxis_tickfont_size=8,
        yaxis=dict(
            titlefont_size=16,
            tickfont_size=8,
        ),

        legend=dict(
            x=0.7,
            y=0.92,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
            font=dict(
                family="Courier New, monospace",
                size=12,
                color="black"
            ),
        ),
        barmode='group',
        bargap=0.15,  # gap between bars of adjacent location coordinates.
        bargroupgap=0.1  # gap between bars of the same location coordinate.
    )

    fig.update_layout(
        title={
            'text': "Main Modules Elapsed Time",
            'y': 0.95,
            'x': 0.95,
            'xanchor': 'right',
            'yanchor': 'top',
        },
        titlefont={
            "size": 12,
            'color': 'black'
        },
    )

    fig.update_layout(template='seaborn',
                        height=400,
                      margin=dict(
                          l=0,
                          r=0,
                          b=0,
                          t=0,
                          pad=0
                      ),
                      )

    return dcc.Graph(id='comp_figure', figure=fig)


def external_table_struct(filename, main):

    main_dict = {}

    main_dict['FILE'] = list(filename)

    for key in main[0].keys():

        main_key_list = []

        for i in range(len(filename)):

            main_key_list.append(round(main[i][key], 1))

        main_dict[key] = main_key_list

    return  main_dict


def external_create_compare_table(filename, main, nltrd3):

    main_dict = external_table_struct(filename, main)

    nltrd3_dict = external_table_struct(filename, nltrd3)

    df_main = pd.DataFrame.from_dict(main_dict)

    df_nltrd3 = pd.DataFrame.from_dict(nltrd3_dict)

    table_main = dash_table.DataTable(
        id='datatable-interactivity-main',
        columns=[
            {"name": i, "id": i} for i in df_main.columns
        ],
        data=df_main.to_dict('records'),
        editable=False,
        sort_action="native",
        sort_mode="single",
        # row_selectable="multi",
        row_deletable=False,
        # selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=5,
        page_count=math.ceil(len(filename) / 5),

        style_cell={'textAlign': 'center', 'padding': '2px', 'font-size': '0.7rem', 'fontWeight': 'bold'},
        # style_as_list_view=True,

        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['CASE', 'DATE']
        ],


        style_header={
            'backgroundColor': 'rgb(210, 230, 230)',
            'fontWeight': 'bold'
        }
    )

    table_nltrd3 = dash_table.DataTable(
        id='datatable-interactivity-main',
        columns=[
            {"name": i, "id": i} for i in df_nltrd3.columns
        ],
        data=df_nltrd3.to_dict('record'),
        editable=False,
        sort_action="native",
        sort_mode="single",
        # row_selectable="multi",
        row_deletable=False,
        # selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=5,
        page_count=math.ceil(len(filename) / 5),

        style_cell={'textAlign': 'center', 'padding': '2px', 'font-size': '0.7rem', 'fontWeight': 'bold'},
        # style_as_list_view=True,

        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['CASE', 'DATE']
        ],


        style_header={
            'backgroundColor': 'rgb(210, 230, 230)',
            'fontWeight': 'bold'
        }
    )

    return table_main, table_nltrd3


@app.callback([Output('output-f04-upload', 'children'),
               Output('ef04_graph_main', 'children'),
               Output('ef04_graph_nltrd3', 'children'),
               Output('ef04_table_main', 'children'),
               Output('ef04_table_nltrd3', 'children')],
              [Input('upload-f04', 'contents')],
              [State('upload-f04', 'filename'),
               State('upload-f04', 'last_modified'),
               State('external-switch', 'value')])
def update_output(list_of_contents, list_of_names, list_of_dates, switch_value):

    print(list_of_names)

    if 1 in switch_value:

        module_print_threshold = 0.0

    else:

        module_print_threshold = 10.0

    flag = 1

    if list_of_contents is not None:

        for filename in list_of_names:

            if 'f04' not in filename:

                flag = 0

                break

        if flag == 0:

            return "Please Select F04 Files ...", [], [], [], []

        else:

            main_set = []

            nltrd3_set = []

            for contents, _, _ in zip(list_of_contents, list_of_names, list_of_dates):

                main = {}

                nltrd3 = {}

                content_type, content_string = contents.split(',')

                decoded = base64.b64decode(content_string)

                lines = str(decoded).split('/n')

                results = module_time_extract(lines)[0]

                main['ELAPSED'] = results['ELAPSED']

                for key in results['MAIN'].keys():

                    main[key] = results['MAIN'][key]

                for key in results['NLTRD3'].keys():

                    nltrd3[key] = results['NLTRD3'][key]

                main_set.append(main)

                nltrd3_set.append(nltrd3)

            main_whole_set = whole_set_process(main_set)

            nltrd3_whole_set = whole_set_process(nltrd3_set)

            main_trace_x, main_trace_y = external_trace_create(main_whole_set, module_print_threshold)

            nltrd3_trace_x, nltrd3_trace_y = external_trace_create(nltrd3_whole_set, module_print_threshold)

            fig_main = external_create_compare_figure(list_of_names, main_trace_x, main_trace_y)

            fig_nltrd3 = external_create_compare_figure(list_of_names, nltrd3_trace_x, nltrd3_trace_y)

            if 2 in switch_value:

                table_main, table_nltrd3 = external_create_compare_table(list_of_names, main_whole_set, nltrd3_whole_set)

            else:

                table_main = []

                table_nltrd3 = []

            return [], fig_main, fig_nltrd3, table_main, table_nltrd3

    else:

        return "Please Select F04 Files to Compare ...", [], [], [], []


def whole_set_process(main_set):

    main_key_com = set()

    for main_i in main_set:

        main_key_com = main_key_com | set(main_i.keys())

    main_whole_set = []

    for main in main_set:

        main_new = {}

        for com_key in main_key_com:

            if com_key in main.keys():

                main_new[com_key] = main[com_key]

            else:

                main_new[com_key] = 0.0

        main_whole_set.append(main_new)

    return main_whole_set


def external_trace_create(main_set, module_print_threshold):

    trace_x_list = []

    trace_y_list = []

    for main in main_set:

        main_sorted = sorted(main.items(), key=lambda a: a[1], reverse=True)

        y_list = []

        x_list = []

        for key in main_sorted:

            if key[1] >= module_print_threshold:

                x_list.append(key[0])

                y_list.append(key[1])

        trace_y_list.append(y_list)

        trace_x_list.append(x_list)

    return trace_x_list, trace_y_list

'''
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/app1':
         return layout1
    elif pathname == '/apps/app2':
         return layout2
    else:
        return '404'
'''

if __name__ == '__main__':

    app.run_server(debug=True, host='0.0.0.0')

