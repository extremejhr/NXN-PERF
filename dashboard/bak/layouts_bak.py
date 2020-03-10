import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import datetime
import plotly.graph_objs as go
import pandas as pd
import dash_table
import math
import data_generator
########## Deploy on shli6056

REG_THRESHOLD = 0.05


class LayoutUpdate(object):

    def __init__(self, tp):

        self.cnames = ['#00BFFF', '#00008B', '#008B8B', '#B8860B', '#006400', '#BDB76B', '#FF8C00', '#8B0000',
                       '#8FBC8F', '#9400D3']

        self.tp = tp

        self.PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    def data_initialize(tp):

        database = data_generator.DataGenerator(tp)
        dfpl = database.table_extract('Plan')
        dfcs = database.table_extract('Case')

        return database, dfpl, dfcs

    def serve_layout():

        return html.Div([navbar, summary_container, case_detail_container])

    def Hex_to_RGB(hex):
        r = int(hex[1:3],16)
        g = int(hex[3:5],16)
        b = int(hex[5:7], 16)
        rgb = str(r)+','+str(g)+','+str(b)
        return rgb

    def generate_table(dataframe, max_rows=100):

        return html.Table(
            # Header
            [html.Thead(html.Tr([html.Th(col) for col in dataframe.columns]))] +

            # Body
            [html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))]
        )


database, dfpl, dfcs = data_initialize('baseline')

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

#dfpl = database.table_extract('Plan')
#dfcs = database.table_extract('Case')

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

nav_item = dbc.NavItem(dbc.NavLink("Link", href="#"))

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(dbc.NavbarBrand("NXN-PERF", className="ml-3")),
                    dbc.Col(
                        dbc.Nav(dbc.NavItem(dbc.NavLink("Case Info", href="#")), className="ml-5", navbar=True),
                        width='auto'
                    ),
                    dbc.Col(
                        dbc.Nav(dbc.NavItem(dbc.NavLink("Perf Compare", href="#")), className="ml-5", navbar=True),
                        width='auto'
                    ),
                    dbc.Col(
                        dbc.Nav(dbc.NavItem(dbc.NavLink("Help", href="#")), className="ml-5", navbar=True),
                        width='auto'
                    ),
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

badge_list = database.key_dict['Case']

cmd = ''

index = 0

bcnames = ['primary', 'success', 'danger', 'warning', 'info']

for badge in badge_list:

    if badge != 'CASE' and badge != 'TEMPLATE':

        if index == 0:

            cmd = "dbc.Badge('" + badge + "', color='" + bcnames[0] + "', pill=True, className='mr-1 mt-2 mb-2', " \
                                                                      "style={'font-size':'0.7rem'})"

        else:

            ind = (index // len(bcnames))

            kp = index - len(bcnames) * ind

            cmd = cmd + ',' + "dbc.Badge('" + badge + "', color='" + bcnames[kp] + "', pill=True, " \
                                                      "className='mr-1 mt-2 mb-2', style={'font-size':'0.7rem'})"

        index = index + 1

badge_cmd = 'html.Span([' + cmd + '])'

case_badges = eval(badge_cmd)

df = dfpl.copy()

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

    if (etime_latest - etime_prev)/etime_prev >= REG_THRESHOLD:

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

    if (etime_latest - etime_baseline)/etime_baseline > REG_THRESHOLD:
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
                          + ", color='danger', bar=True)], multi=True, style={'font-size':'0.3rem', 'height': '30px'}),"

else:

    process_bar_cmd_lp = "dbc.Progress([dbc.Progress(children='" + str(100 - perf_increase_lp) + "%', value=" \
                         + str(100-perf_increase_lp) + ", color='success', bar=True)," \
                          + "dbc.Progress(children='" + str(perf_increase_lp) + "%', value=" + str(perf_increase_lp) \
                          + ", color='warning', bar=True)], multi=True, style={'font-size':'0.3rem', 'height': '30px'}),"

if perf_increase_lb < 0:

    process_bar_cmd_lb = "dbc.Progress([dbc.Progress(children='" + str(100) + "%', value=" \
                         + str(100-abs(perf_increase_lb)) + ", color='warning', bar=True)," \
                          + "dbc.Progress(children='" + str(abs(perf_increase_lb)) + "%', value=" + str(perf_increase_lb) \
                          + ", color='danger', bar=True)], multi=True, style={'font-size':'0.3rem', 'height': '30px'}),"

else:

    process_bar_cmd_lb = "dbc.Progress([dbc.Progress(children='" + str(100 - perf_increase_lb) + "%', value=" \
                         + str(100-perf_increase_lb) + ", color='success', bar=True)," \
                          + "dbc.Progress(children='" + str(perf_increase_lb) + "%', value=" + str(perf_increase_lb) \
                          + ", color='warning', bar=True)], multi=True, style={'font-size':'0.3rem', 'height': '30px'}),"

lp_process = eval(process_bar_cmd_lp)
lb_process = eval(process_bar_cmd_lb)

dfc = dfcs.copy()

orderc = ['CASE', 'TEMPLATE']

for dfc_key in database.key_dict['Case']:

    if dfc_key != 'CASE' and dfc_key != 'TEMPLATE':

        orderc.append(dfc_key)

dfc = dfc[orderc]

table_case = dbc.Table(
    # using the same table as in the above example
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
            "height": 500,
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
            "height": 500,
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

dfr = dfpl.copy()

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
    generate_table(dfrb),
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
    generate_table(dfrp),
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
                dbc.ModalHeader("Performance Regression Cases"),
                dbc.ModalBody(
                    [
                        dbc.Jumbotron(
                            [
                                dbc.Row(
                                    [
                                        html.H6('Regression Cases compared with Previous Group')
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
                                        dbc.Col(html.H4(str(latest_elapsed_lb), className="card-title",
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
                                        dbc.Col(html.H4(str(baseline_elapsed), className="card-title",
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
                                        dbc.Col(html.H4(str(latest_elapsed_lp), className="card-title",
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
                                        dbc.Col(html.H4(str(prev_elapsed), className="card-title",
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
                                style={'font-size':'0.3rem', 'height': '30px'},
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

                                    dbc.Row(dbc.Col(
                                        html.H6("Performance Testing Summary for Latest Group (" + latest_group + ")"),
                                            className='mb-4 mt-3', style={
                                            'color': 'grey'
                                        })),

                                    dbc.Row(
                                        [
                                            dbc.Col(dbc.Card(case_card_content, color="success mb-3", outline=True,
                                                             style= {'min-width':'310px'})),
                                            dbc.Col(dbc.Card(time_card_content, color="primary mb-3", outline=True,
                                                             style= {'min-width':'255px'})),
                                            dbc.Col(dbc.Card(time_card_content1, color="info mb-3", outline=True,
                                                             style= {'min-width':'255px'})),
                                            dbc.Col(dbc.Card(time_card_content2, color="danger mb-3", outline=True,
                                                             style= {'min-width':'252px'})),
                                        ],

                                        className="mb-2",
                                        justify="center",
                                        align="center",
                                    ),
                        ],
                        className='mt-5 jumbotron',
                    ),
                width=11,
                ),
            ],
            justify="center",
            align="center",
            style={
                'background-color': '#f8f9fa'
            }
        )

df = dfpl.copy()

df = df.sort_values(by="GROUP", ascending=False)

df['index'] = range(1, len(df) + 1)

df.drop('RESULT', axis=1)

order = ['index', 'DATE', 'CASE', 'GROUP', 'ELAPSED']

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
    sort_mode="multi",
    #row_selectable="multi",
    row_deletable=False,
    #selected_rows=[],
    page_action="native",
    page_current=0,
    page_size=PAGE_SIZE,
    page_count=math.ceil(df.shape[0]/PAGE_SIZE),

    style_cell={'textAlign': 'center', 'padding': '5px'},
    style_as_list_view=True,

    style_cell_conditional=[
        {
            'if': {'column_id': c},
            'textAlign': 'left'
        } for c in ['CASE', 'DATE']
    ],

    style_data_conditional=[
        {'if': {'column_id': 'index'},
         'width': '50px'},
        {'if': {'column_id': 'DATE'},
         'width': '100px'},
        {'if': {'column_id': 'CASE'},
         'width': '100px'},
        {'if': {'column_id': 'GROUP'},
         'width': '70px'},
        {'if': {'column_id': 'ELAPSED'},
         'width': '100px'},
    ],
    style_header={
        'backgroundColor': 'rgb(210, 230, 230)',
        'fontWeight': 'bold'
    }
)
# Add data

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

graph1 = dcc.Graph(id='histroy_elapsed')

showing_graph =html.Div(id='vision_box', children=spinners)

case_detail_container = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Jumbotron(
                        [
                            dbc.Row(
                                html.H6("Performance Testing History"),
                                className='mb-4 mt-3', style={
                                    'color': 'grey'
                                }),
                            dbc.Row(
                                [
                                    dbc.Col(table1, style={'margin': 'auto'})
                                ],
                            style={'min-height': '600px'}
                            )
                        ],
                        className='mt-2 jumbotron',
                    ),
                width=6,
                style={'min-width': '750px'}
                ),

                dbc.Col(
                    dbc.Jumbotron(
                        [
                            dbc.Row(
                                html.H6("Performance Curve"),
                                className='mb-4 mt-3', style={
                                    'color': 'grey'
                                }),
                            dbc.Row(
                                [
                                    dbc.Col(showing_graph, width='12')
                                ],
                            style={'min-height': '600px'}
                            )
                        ],
                        className='mt-2 jumbotron'
                ),
                width=5,
                style={'min-width': '500px'}
                )
            ],
            justify="center",
            align="start",
            style={
                'background-color': '#f8f9fa'
            }
        )
    ]
)

