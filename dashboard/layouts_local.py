import sys

sys.path.append('../bin/')

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import datetime
import plotly.graph_objs as go
import pandas as pd
import dash_table
import math
import data_generator
import globalvar as gl
########## Deploy on shli6056


class LayoutUpdate(object):

    def __init__(self, tp):

        self.REG_THRESHOLD = 0.1

        self.cnames = ['#00BFFF', '#00008B', '#008B8B', '#B8860B', '#006400', '#BDB76B', '#FF8C00', '#8B0000',
                       '#8FBC8F', '#9400D3']

        self.PAGESIZE = 15

        self.tp = tp

        self.PLOTLY_LOGO = ".\\assets\\img\\logo3.png"

        self.database = data_generator.DataGenerator(self.tp)

        self.dfpl = self.database.table_extract('Plan')

        self.dfcs = self.database.table_extract('Case')

        self.dfmn = self.database.table_extract('Main')

        self.dfnl3 = self.database.table_extract('Nltrd3')

        gl.set_value('dfpl', self.dfpl)

        gl.set_value('dfcs', self.dfcs)

        gl.set_value('dfmn', self.dfmn)

        gl.set_value('dfnl3', self.dfnl3)

        gl.set_value('range_group', 6)

        self.key_dict = self.database.key_dict

    def generate_table(self, dataframe, max_rows=100):

        return html.Table(
            # Header
            [html.Thead(html.Tr([html.Th(col) for col in dataframe.columns]))] +

            # Body
            [html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))]
        )

    def container_generator(self):

        search_bar = dbc.Row(
            [
                dbc.Col(dbc.Input(type="search", placeholder="Search")),
                dbc.Col(
                    dbc.Button("Search", color="primary", className="ml-2"),
                    width="auto",
                ),
            ],
            no_gutters=True,
            className="ml-auto flex-nowrap mt-3 mt-md-0",
            align="center",
        )

        navbar = dbc.Navbar(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=self.PLOTLY_LOGO, height="35px")),
                            dbc.Col(dbc.NavbarBrand("NXN-PERF", className="ml-2")),
                        ],
                        align="center",
                        no_gutters=True,
                    ),
                    href="https://plot.ly",
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
            ],
            color="primary",
            dark=True,
        )

        badge_list = self.key_dict['Case']

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

        df = self.dfpl.copy()

        group_sorted = df.sort_values(by="GROUP", ascending=False)

        latest_group = group_sorted.max().GROUP

        baseline_group = group_sorted.min().GROUP

        prev_group = group_sorted.loc[group_sorted['GROUP'] < latest_group].GROUP[0]

        latest_case_number = df.loc[df['GROUP'] == latest_group].shape[0]

        cases = {}

        group = df.groupby('CASE').groups

        for i in range(len(df)):

            group_list = []

            elapsed_list = []

            for item in group[df.loc[i, 'CASE']]:

                group_list.append(df.loc[item, 'GROUP'])

                elapsed_list.append(df.loc[item, 'ELAPSED'])

            cases[df.loc[i, 'CASE']] = [group_list, elapsed_list]

        elp_case = []

        elb_case = []

        for key in cases.keys():

            if latest_group in cases[key][0] and prev_group in cases[key][0]:

                elp_case.append(key)

            if latest_group in cases[key][0] and baseline_group in cases[key][0]:

                elb_case.append(key)

        latest_elapsed_lp = 0.0

        latest_elapsed_lb = 0.0

        prev_elapsed = 0.0

        baseline_elapsed = 0.0

        latest_elapsed_lp_list = []

        latest_elapsed_lb_list = []

        prev_elapsed_list = []

        baseline_elapsed_list = []

        reg_latest_elapsed_lp_list = []

        reg_latest_elapsed_lb_list = []

        reg_prev_elapsed_list = []

        reg_baseline_elapsed_list = []

        reg_lp_case = []

        reg_lb_case = []

        for ct in elp_case:

            etime_latest = df.loc[(df['GROUP'] == latest_group) & (df['CASE'] == ct)].sum().ELAPSED

            etime_prev = df.loc[(df['GROUP'] == prev_group) & (df['CASE'] == ct)].sum().ELAPSED

            latest_elapsed_lp = latest_elapsed_lp + etime_latest

            prev_elapsed = prev_elapsed + etime_prev

            latest_elapsed_lp_list.append(etime_latest)

            prev_elapsed_list.append(etime_prev)

            if (etime_latest - etime_prev)/etime_prev >= self.REG_THRESHOLD:

                reg_lp_case.append(ct)

                reg_latest_elapsed_lp_list.append(etime_latest)

                reg_prev_elapsed_list.append(etime_prev)

        for ct in elb_case:

            etime_latest = df.loc[(df['GROUP'] == latest_group) & (df['CASE'] == ct)].sum().ELAPSED

            etime_baseline = df.loc[(df['GROUP'] == baseline_group) & (df['CASE'] == ct)].sum().ELAPSED

            latest_elapsed_lb = latest_elapsed_lb + etime_latest

            baseline_elapsed = baseline_elapsed + etime_baseline

            latest_elapsed_lb_list.append(etime_latest)

            baseline_elapsed_list.append(etime_baseline)

            if (etime_latest - etime_baseline)/etime_baseline > self.REG_THRESHOLD:
                reg_lb_case.append(ct)

                reg_latest_elapsed_lb_list.append(etime_latest)

                reg_baseline_elapsed_list.append(etime_baseline)

        latest_elapsed_lp = round(latest_elapsed_lp/60.0, 1)

        latest_elapsed_lb = round(latest_elapsed_lb/60.0, 1)

        prev_elapsed = round(prev_elapsed/60.0, 1)

        baseline_elapsed = round(baseline_elapsed/60.0, 1)

        perf_increase_lp = round((prev_elapsed - latest_elapsed_lp) / prev_elapsed * 100, 1)

        perf_increase_lb = round((baseline_elapsed - latest_elapsed_lb) / baseline_elapsed * 100, 1)

        if perf_increase_lp < 0:

            process_bar_cmd_lp = "dbc.Progress([dbc.Progress(children='" + str(100) + "%', value=" \
                                 + str(100-abs(perf_increase_lp)) + ", color='warning', bar=True)," \
                                  + "dbc.Progress(children='" + str(abs(perf_increase_lp)) + "%', value=" + str(perf_increase_lp) \
                                  + ", color='danger', bar=True)], multi=True, style={'font-size':'0.8rem', 'height': '35px'}),"

        else:

            process_bar_cmd_lp = "dbc.Progress([dbc.Progress(children='" + str(100 - perf_increase_lp) + "%', value=" \
                                 + str(100-perf_increase_lp) + ", color='success', bar=True)," \
                                  + "dbc.Progress(children='" + str(perf_increase_lp) + "%', value=" + str(perf_increase_lp) \
                                  + ", color='warning', bar=True)], multi=True, style={'font-size':'0.8rem', 'height': '35px'}),"

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

        lp_process = eval(process_bar_cmd_lp)
        lb_process = eval(process_bar_cmd_lb)

        dfc = self.dfcs.copy()

        orderc = ['CASE', 'TEMPLATE']

        for dfc_key in self.key_dict['Case']:

            if dfc_key != 'CASE' and dfc_key != 'TEMPLATE':

                orderc.append(dfc_key)

        dfc = dfc[orderc]

        table_case = dbc.Table(
            # using the same table as in the above example
            self.generate_table(dfc),
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

        trace_lb_latest = go.Bar(x=elb_case, y=latest_elapsed_lb_list, name=latest_group)
        trace_lp_latest = go.Bar(x=elp_case, y=latest_elapsed_lp_list, name=latest_group)
        trace_baseline = go.Bar(x=elb_case, y=baseline_elapsed_list, name=baseline_group)
        trace_prev = go.Bar(x=elp_case, y=prev_elapsed_list, name=prev_group)

        trace_lb = [trace_baseline, trace_lb_latest]

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

        trace_lp = [trace_prev, trace_lp_latest]

        otp_graph = dcc.Graph(
            id='otp_graph',
            figure={
                "data": trace_lp,
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                    },
                    "height": 400,
                    "margin": {"t": 10, "l": 10, "r": 10},
                    "legend": dict(x=0.0, y=1.0),
                },
            },
        )

        otp_modal = html.Div(
            [
                dbc.Button("View Detail", id="otp_open", color='info', outline=True, block=True, className='btn-sm'),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Overall Time Compared with Previous Group"),
                        dbc.ModalBody(
                            [
                                dbc.Jumbotron(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(otp_graph, width=12)
                                            ]
                                        )
                                    ]
                                )
                            ],
                            style={'margin': 'auto'}),
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

        reg_trace_prev = go.Bar(x=reg_lp_case, y=reg_prev_elapsed_list, name=prev_group)
        reg_trace_lp_latest = go.Bar(x=reg_lp_case, y=reg_latest_elapsed_lp_list, name=latest_group)
        reg_trace_lp = [reg_trace_prev, reg_trace_lp_latest]

        reg_trace_baseline = go.Bar(x=reg_lb_case, y=reg_baseline_elapsed_list, name=baseline_group)
        reg_trace_lb_latest = go.Bar(x=reg_lp_case, y=reg_latest_elapsed_lp_list, name=latest_group)
        reg_trace_lb = [reg_trace_baseline, reg_trace_lb_latest]

        reg_graph_lb = dcc.Graph(
            id='reg_graph_lb',
            figure={
                "data": reg_trace_lb,
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

        dfr = self.dfpl.copy()

        dfrb = dfr.copy().loc[dfr['CASE'].isin(list(set(reg_lb_case)))]

        dfrp = dfr.copy().loc[dfr['CASE'].isin(list(set(reg_lp_case)))]

        dfrb['index'] = range(1, len(dfrb) + 1)
        dfrp['index'] = range(1, len(dfrp) + 1)

        dfrb.drop('RESULT', axis=1)
        dfrp.drop('RESULT', axis=1)

        orderr = ['index', 'DATE', 'CASE', 'GROUP', 'ELAPSED']

        dfrb = dfrb[orderr]
        dfrp = dfrp[orderr]

        table_reg_case_b = dbc.Table(
            # using the same table as in the above example
            self.generate_table(dfrb),
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
            className='table-danger'
        )

        if len(reg_lp_case) == 0:

            Reg_Flag = True

        else:

            Reg_Flag = False

        table_reg_case_p = dbc.Table(
            # using the same table as in the above example
            self.generate_table(dfrp),
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

        case_card_content = [

            dbc.CardHeader("Testing Cases", id="TestCase", style={'font-size': '0.8rem', 'color':'grey', 'font-weight':'bold'}),

            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(html.H5(str(latest_case_number) + " Cases", className="card-title", style={'color':'green'})),
                        ],
                        className='mb-1'
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                html.P(
                                    "tested in last performance test.",
                                    className="text-muted",
                                    style={
                                        'color': 'grey',
                                        'font-size': '0.9rem'
                                    }
                                ),
                            ),
                        ],
                        className='mt-2'
                    ),
                    dbc.Row(
                        [
                            dbc.Col(case_badges),
                        ],
                        className='mt-1'
                    ),
                    dbc.Row(
                        [
                            dbc.Col(case_modal, width=12),
                        ],
                        className='mt-3'
                    ),
                ]
            ),
        ]

        time_card_content = [

            dbc.CardHeader("Overall Time vs Baseline", style={'font-size': '0.8rem', 'color':'grey','font-weight':'bold'}),

            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H5(latest_group, className="card-title",
                                                                style={'color': 'grey', 'font-size':'80%'}), width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H5(str(latest_elapsed_lb), className="card-title",
                                                                style={'color': 'green'}), width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H6("Minutes", className="card-title",
                                                                style={'color': 'dark', 'font-size':'70%'}), width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                    ],
                                ),
                            width='auto'),

                            dbc.Col(
                                html.Div(
                                    [

                                        dbc.Row(
                                            [
                                                dbc.Col(html.H6("vs", className="card-title", style={'color': 'dark'}),
                                                        width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                    ]
                                ),
                                width='auto'),

                            dbc.Col(
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H5(baseline_group, className="card-title",
                                                                style={'color': 'grey', 'font-size': '80%'}), width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H5(str(baseline_elapsed), className="card-title",
                                                                style={'color': '#f0ad4e'}), width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H6("Minutes", className="card-title",
                                                                style={'color': 'dark', 'font-size': '70%'}), width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                    ]
                                ),
                            width='auto')
                        ],
                        justify='center',
                        align='center'
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                lb_process
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(otb_modal, className='mt-3'),
                        ]
                    ),
                ]
            ),
        ]

        time_card_content1 = [

            dbc.CardHeader("Overall Time vs Prev. Group", style={'font-size': '0.8rem', 'color':'grey','font-weight':'bold'}),

            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H5(latest_group, className="card-title",
                                                                style={'color': 'grey', 'font-size':'80%'}), width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H5(str(latest_elapsed_lp), className="card-title",
                                                                style={'color': 'green'}), width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H6("Minutes", className="card-title",
                                                                style={'color': 'dark', 'font-size':'70%'}), width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                    ],
                                ),
                            width='auto'),

                            dbc.Col(
                                html.Div(
                                    [

                                        dbc.Row(
                                            [
                                                dbc.Col(html.H6("vs", className="card-title", style={'color': 'dark'}),
                                                        width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                    ]
                                ),
                                width='auto'),

                            dbc.Col(
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H5(prev_group, className="card-title",
                                                                style={'color': 'grey', 'font-size': '80%'}), width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H5(str(prev_elapsed), className="card-title",
                                                                style={'color': '#f0ad4e'}), width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(html.H6("Minutes", className="card-title",
                                                                style={'color': 'dark', 'font-size': '70%'}), width='auto'),
                                            ],
                                            justify='center',
                                            align='center'
                                        ),
                                    ]
                                ),
                            width='auto')
                        ],
                        justify='center',
                        align='center'
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                    lp_process
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(otp_modal, className='mt-3'),
                        ]
                    ),
                ]
            ),
        ]

        time_card_content2 = [

            dbc.CardHeader("New Regression Cases", style={'font-size': '0.8rem', 'color':'grey','font-weight':'bold'}),

            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(html.H5(str(len(reg_lp_case)) + " Cases", className="card-title", style={'color':'#d43f3a'})),
                        ],
                        className='mb-1'
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                html.P(
                                    "found regression in last testing.",
                                    className="text-muted",
                                    style={
                                        'color': 'grey',
                                        'font-size': '0.9rem'
                                    }
                                ),
                            ),
                        ],
                        className='mt-1'
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                    dbc.Progress(
                                        [
                                            dbc.Progress(children=str(latest_case_number-len(reg_lp_case)) + ' Cases',
                                                         value=(latest_case_number-len(reg_lp_case))/latest_case_number * 100,
                                                         color='success', bar=True),

                                            dbc.Progress(children=str(len(reg_lp_case)),
                                                         value=(len(reg_lp_case)) / latest_case_number*100,
                                                         color='danger', bar=True),
                                        ],
                                        multi=True,
                                        style={'font-size':'0.8rem', 'height': '30px'},
                                        className='mt-3'
                                    )
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(reg_modal, className='mt-3'),
                        ]
                    ),
                ]
            ),
        ]

        summary_container = dbc.Row(
                    [
                        dbc.Col
                        (
                            dbc.Jumbotron(
                                [

                                            dbc.Row(
                                                [
                                                    dbc.Col(html.Img(src='.\\assets\\img\\summary-icon.png', height="30px"),
                                                            width='auto', style={'margin': 'auto'}),
                                                    dbc.Col(html.H6("Performance Testing Summary for Latest Group (" + latest_group + ")",
                                                                    style={'font-size': '85%'}),
                                                        className='mt-3 ml-3', style={
                                                        'color': 'grey'
                                                    })
                                                ],
                                                justify='between',
                                                align='center',
                                                no_gutters=True,
                                            ),
                                            html.Hr(),
                                            dbc.Row(
                                                [
                                                    dbc.Col(dbc.Card(case_card_content, color="success mb-3", outline=True,
                                                                     style= {'min-width':'15.6rem'})),
                                                    dbc.Col(dbc.Card(time_card_content, color="primary mb-3", outline=True,
                                                                     style= {'min-width':'15.6rem'})),
                                                    dbc.Col(dbc.Card(time_card_content1, color="info mb-3", outline=True,
                                                                     style= {'min-width':'15.6rem'})),
                                                    dbc.Col(dbc.Card(time_card_content2, color="danger mb-3", outline=True,
                                                                     style= {'min-width':'15.6rem'})),
                                                ],
                                                justify="center",
                                                align="center",
                                                style={'width': '104%', 'margin-left': '-2rem'}
                                            ),
                                ],
                                className='mt-5 jumbotron',
                            ),
                        width=12,
                        ),
                    ],
                    justify="center",
                    align="center",
                    style={
                        'background-color': '#4582EC'
                    }
                )

        df = self.dfpl.copy()

        df = df.sort_values(by="GROUP", ascending=False)

        df['index'] = range(1, len(df) + 1)

        df.drop('RESULT', axis=1)

        order = ['DATE', 'CASE', 'GROUP', 'ELAPSED']

        df = df[order]

        PAGE_SIZE = self.PAGESIZE

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

        showing_graph = html.Div(id='vision_box', children=spinners)

        case_detail_container = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Jumbotron(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(html.Img(src='.\\assets\\img\\perf-history.png', height="30px"),
                                                    width='auto', style={'margin': 'auto', 'margin-left': '-1rem'}),
                                            dbc.Col(html.H6(
                                                "Performance Testing History",
                                                style={'font-size': '85%'}),
                                                    className='mt-2 ml-2', style={
                                                    'color': 'grey'
                                                })
                                        ],
                                        justify='start',
                                        align='center',
                                        no_gutters=True,
                                    ),
                                    html.Hr(),
                                    dbc.Row(
                                        [
                                            dbc.Col(table1, style={'margin-left': 'auto', 'margin-right': 'auto'})
                                        ],
                                    style={'min-height': '37.5rem'}
                                    )
                                ],
                                className='mt-1 jumbotron',
                            ),
                        width=6,
                        md=12,
                        lg=6,
                        style={'min-width': '40rem'}
                        ),

                        dbc.Col(
                            dbc.Jumbotron(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(html.Img(src='.\\assets\\img\\perf-curve.png', height="30px"),
                                                    width='auto', style={'margin': 'auto', 'margin-left': '-1rem'}),
                                            dbc.Col(html.H6(
                                                "Performance Curve",
                                                style={'font-size': '85%'}),
                                                    className='mt-2 ml-2', style={
                                                    'color': 'grey'
                                                })
                                        ],
                                        justify='between',
                                        align='center',
                                        no_gutters=True,
                                    ),
                                    html.Hr(),
                                    dbc.Row(
                                        [
                                            dbc.Col(showing_graph, width='12')
                                        ],
                                    style={'height': '37.5rem'}
                                    )
                                ],
                                className='mt-1 jumbotron',
                        ),
                        width=6,
                        md=12,
                        lg=6,
                        style={'min-width': '15.25rem'}
                        )
                    ],
                    justify="center",
                    align="start",
                    style={
                        'background-color': '#4582EC'
                    }
                )
            ]
        )

        main_content = html.Div([summary_container, case_detail_container])

#############################################################

        dfgp = self.dfpl.copy()

        gl.set_value('group_key', dfgp.groupby('GROUP').groups)

        group_key = dfgp.groupby('GROUP').groups.keys()

        group_list = []

        for key in list(group_key):

            group_list.append({"label": key, "value": key})

        group_options = group_list

        input_groups = html.Div(
            [
                dbc.FormGroup(
                        [
                            dbc.Label("Select Groups"),
                            dcc.Dropdown(id="group-multi-dynamic-dropdown", placeholder="Input group number ...",
                                         multi=True, options=group_options),
                            dbc.FormText("Input keyword above and select groups."),
                        ],
                    style={'font-size':'0.9rem'}
                ),
                dbc.FormGroup(
                    [
                        dbc.Label("Select Case"),
                        dcc.Dropdown(id="case-single-dynamic-dropdown", placeholder="Input case name ...", multi=False, disabled=False),
                        dbc.FormText("Input keyword above and select case."),
                    ],
                    style={'font-size': '0.9rem'}
                ),
                dbc.FormGroup(
                    [
                        dbc.Checklist(
                            options=[
                                {"label": "List All Modules/Sub-modules", "value": 1},
                                {"label": "Print Perf. Table Data", "value": 2},
                            ],
                            value=[],
                            id="switches-inline-input",
                            inline=False,
                            switch=True,
                        ),
                    ],
                    style={'font-size': '0.9rem'}
                ),
                dbc.Button("Start Compare", id="search_start", color='success', outline=True, block=True, className='mt-3'),
            ],
            style={'min-height': '20rem'}
        )

        compare_graph = html.Div(dbc.Card(
            [
                html.Div(
                    [
                        dbc.CardImg(src=".\\assets\\img\\perf_compare_main7.png", top=True, style={'width': '100%',
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

        compare_graph1 = html.Div(dbc.Card(
            [
                html.Div(
                    [
                        dbc.CardImg(src=".\\assets\\img\\perf_compare_main7.png", top=True, style={'width': '100%',
                                                                                                   'height': '100%'}),
                    ],
                ),
                dbc.CardBody(
                    [
                        html.H6("NLTRD3 Submodules Elapsed Time", className="card-title", style={'font-size': '80%'}),
                        html.P(
                            "The elapsed time of sub-modules of NLTRD3 will be ploted here.",
                            className="card-text",
                            style={'font-size': '0.5rem'}
                        ),
                    ]
                )
            ],
            color='success',
            inverse=True
        ),
            id="compare_graph1",
        )
        compare_table = html.Div(id='compare_table')

        compare_table1 = html.Div(id='compare_table1')

        search_area = dbc.Row(
                    [
                        dbc.Col
                        (
                            dbc.Jumbotron(
                                [

                                            dbc.Row(
                                                [
                                                    dbc.Col(html.Img(src='.\\assets\\img\\search.png', height="35px"),
                                                            width='auto', style={'margin': 'auto'}),
                                                    dbc.Col(html.H6("Performance Comparision",
                                                                    style={'font-size': '85%'}),
                                                        className='mt-2 ml-3', style={
                                                        'color': 'grey'
                                                    })
                                                ],
                                                justify='between',
                                                align='center',
                                                no_gutters=True,
                                            ),
                                            html.Hr(),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        dbc.Card(
                                                            [
                                                                dbc.CardHeader(html.H6("Select Comparing Cases and Groups",
                                                                                       style={'font-size': '80%'})),
                                                                dbc.CardBody([input_groups])
                                                            ]
                                                        ),
                                                        width=4,
                                                    ),
                                                    dbc.Col(compare_graph, width=4),
                                                    dbc.Col(compare_graph1, width=4),
                                                ],
                                                justify="start",
                                                align="center",
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(compare_table, width=12, className='mt-3')
                                                ]
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(compare_table1, width=12, className='mt-3')
                                                ]
                                            ),
                                ],
                                className='mt-5 jumbotron',
                            ),
                        width=12,
                        ),
                    ],
                    justify="center",
                    align="center",
                    style={
                        'background-color': '#4582EC'
                    }
                )

        dftg = self.dfpl.copy()

        groups = list(dftg.groupby('GROUP').groups.keys())

        gl.set_value('total_groups', groups)

        groups = ['1899.116', '1926.32', '1926.43', '1926.52', '1926.60', '1926.66', '1926.70', '1926.80', '1926.88',
                  '1926.90', '1926.110', '1926.125', '1926.135', '1926.145', '1926.150', '1926.160', '1926.170', '1926.180']

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

        group_range = dcc.RangeSlider(
                                    count=1,
                                    min=0,
                                    max=range_max,
                                    value=[0, range_max],
                                    marks={i: groups[range_labels[i]] for i in range(len(range_labels))},
                                    id='group_range'
                                )

        track_plot = html.Div(id="track_plot")

        trending_groups = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.FormGroup(
                                [
                                    dbc.Label("From Group"),
                                    dcc.Dropdown(id="trend_group_start", placeholder="Select group number ...",
                                                 multi=False, disabled=False, options=gopts),
                                    dbc.FormText("Input keyword above and select case."),
                                ],
                                style={'font-size': '0.9rem'}
                            ),
                        ),
                        dbc.Col(
                            dbc.FormGroup(
                                [
                                    dbc.Label("To Group"),
                                    dcc.Dropdown(id="trend_group_end", placeholder="Select group number ...",
                                                 multi=False, disabled=False, options=gopts),
                                    dbc.FormText("Input keyword above and select case."),
                                ],
                                style={'font-size': '0.9rem'}
                            ),
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(group_range, className='mt-1 mb-2')
                    ],
                ),

                dbc.Row(
                    [
                        dbc.FormGroup(
                            [
                                dbc.Checklist(
                                    options=[
                                        {"label": "Only Plot Start and End Group", "value": 1},
                                    ],
                                    value=[],
                                    id="switches-inline-input11",
                                    inline=False,
                                    switch=True,
                                ),
                            ],
                            style={'font-size': '0.9rem'}
                        ),
                    ],
                    className='mt-2'
                ),
                dbc.Row(
                    [
                        dbc.Button("Start Track", id="search_track", color='success', outline=True, block=True,
                                   className='mt-2'),
                    ]
                ),

                dbc.Row(
                    [
                        dbc.Col(track_plot)
                    ]
                )
            ],
            style={'min-height': '16rem'}
        )

        trending_area = dbc.Row(
            [
                dbc.Col
                    (
                    dbc.Jumbotron(
                        [

                            dbc.Row(
                                [
                                    dbc.Col(html.Img(src='.\\assets\\img\\trending.png', height="35px"),
                                            width='auto', style={'margin': 'auto'}),
                                    dbc.Col(html.H6("Performance Tracking",
                                                    style={'font-size': '85%'}),
                                            className='mt-2 ml-3', style={
                                            'color': 'grey'
                                        })
                                ],
                                justify='between',
                                align='center',
                                no_gutters=True,
                            ),
                            html.Hr(),
                            dbc.Row(
                                [
                                    dbc.Col(trending_groups)
                                ],
                            )
                        ],
                        className='mt-2 jumbotron',
                    ),
                    width=12,
                ),
            ],
            justify="center",
            align="center",
            style={
                'background-color': '#4582EC'
            }
        )

        testplan_area = dbc.Row(
            [
                dbc.Col
                    (
                    dbc.Jumbotron(
                        [

                            dbc.Row(
                                [
                                    dbc.Col(html.Img(src='.\\assets\\img\\testplan.png', height="35px"),
                                            width='auto', style={'margin': 'auto'}),
                                    dbc.Col(html.H6("Testing Plan Matrix",
                                                    style={'font-size': '85%'}),
                                            className='mt-2 ml-3', style={
                                            'color': 'grey'
                                        })
                                ],
                                justify='between',
                                align='center',
                                no_gutters=True,
                            ),
                            html.Hr(),
                        ],
                        className='mt-2 jumbotron',
                    ),
                    width=12,
                ),
            ],
            justify="center",
            align="center",
            style={
                'background-color': '#4582EC'
            }
        )

        lab_dash = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(trending_area, width=6),
                        dbc.Col(testplan_area, width=6),
                    ]
                )
            ]
        )

        perf_compare_content = html.Div([search_area, lab_dash])

#############################################################

        main_card = dbc.Jumbotron(
            [
                dbc.Card(
                    [
                        dbc.CardHeader(
                            dbc.Tabs(
                                [
                                    dbc.Tab(label="Summary", tab_id="Summary", children=main_content,
                                            tab_style={"margin-left": "0.5rem"}),
                                    dbc.Tab(label="Perf-Lab", tab_id="Perf-Compare", children=perf_compare_content,
                                            tab_style={"margin-left": "0.5rem"}),
                                ],
                                id="card-tabs",
                                card=True,
                                active_tab="Summary",
                                style={'color': 'white'},
                                className='ml-1',
                            )
                        ),
                        #dbc.CardBody(id='tab_content', children=main_content),
                    ],
                    color='primary',
                    style={
                        'background-color': '#4582EC'
                    },
                    className='mt-3'
                )
            ]
        )

        Main_Container = [navbar, main_card]

        return Main_Container

