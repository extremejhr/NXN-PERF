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
import globalvar as gl
########## Deploy on shli6056

REG_THRESHOLD = 0.05

PAGESIZE = 16


def container_generator():

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
                        dbc.Col(html.Img(src="./assets/img/logo3.png", height="35px")),
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

    case_card_content = [

        dbc.CardHeader("Testing Cases", id="TestCase", style={'font-size': '0.8rem', 'color':'grey', 'font-weight':'bold'}),

        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(html.H5(id='case_number', className="card-title", style={'color':'green'})),
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
                        dbc.Col(html.Div(id='case_badges')),
                    ],
                    className='mt-1'
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Div(id='case_modal'), width=12),
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
                                            dbc.Col(html.H5(id='latest_group_lb', className="card-title",
                                                            style={'color': 'grey', 'font-size':'80%'}), width='auto'),
                                        ],
                                        justify='center',
                                        align='center'
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(html.H5(id='latest_elapsed_lb', className="card-title",
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
                                            dbc.Col(html.H5(id='baseline_group_lb', className="card-title",
                                                            style={'color': 'grey', 'font-size': '80%'}), width='auto'),
                                        ],
                                        justify='center',
                                        align='center'
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(html.H5(id='baseline_elapsed_lb', className="card-title",
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
                        dbc.Col(html.Div(id='lb_process')),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Div(id='otb_modal'), className='mt-3'),
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
                                            dbc.Col(html.H5(id='latest_group_lp', className="card-title",
                                                            style={'color': 'grey', 'font-size':'80%'}), width='auto'),
                                        ],
                                        justify='center',
                                        align='center'
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(html.H5(id='latest_elapsed_lp', className="card-title",
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
                                            dbc.Col(html.H5(id='prev_group_lp', className="card-title",
                                                            style={'color': 'grey', 'font-size': '80%'}), width='auto'),
                                        ],
                                        justify='center',
                                        align='center'
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(html.H5(id='prev_elapsed_lp', className="card-title",
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
                        dbc.Col(html.Div(id='lp_process')),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Div(id='otp_modal'), className='mt-3'),
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
                        dbc.Col(html.H5(id='reg_case_number', className="card-title", style={'color':'#d43f3a'})),
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
                        dbc.Col(html.Div(id='reg_progress')),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(id='reg_modal', className='mt-3'),
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
                                                dbc.Col(html.Img(src='./assets/img/summary-icon.png', height="30px"),
                                                        width='auto', style={'margin': 'auto'}),
                                                dbc.Col(html.H6("Performance Testing Summary for Latest Group",
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

    case_detail_container = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Jumbotron(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(html.Img(src='./assets/img/perf-history.png', height="30px"),
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
                                        dbc.Col(html.Div(id='history_table'), style={'margin-left': 'auto', 'margin-right': 'auto'})
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
                                        dbc.Col(html.Img(src='./assets/img/perf-curve.png', height="30px"),
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
                                        dbc.Col(html.Div(id='showing_graph', style={'height':'20rem'}), width='12')
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

    input_groups = html.Div(
        [
            dbc.FormGroup(
                    [
                        dbc.Label("Select Groups"),
                        dcc.Dropdown(id="group-multi-dynamic-dropdown", placeholder="Input group number ...",
                                     multi=True),
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

    compare_graph1 = html.Div(dbc.Card(
        [
            html.Div(
                [
                    dbc.CardImg(src="./assets/img/perf_compare_main7.png", top=True, style={'width': '100%',
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
                                                dbc.Col(html.Img(src='./assets/img/search.png', height="35px"),
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

    group_range = html.Div(id='group_range')

    track_plot = html.Div(dbc.Card(
        [
            html.Div(
                [
                    dbc.CardImg(src="./assets/img/perf_compare_main7.png", top=True, className='img-fluid'),
                ],
            ),
            dbc.CardBody(
                [
                    html.H6("Total Elapsed Time", className="card-title", style={'font-size': '80%'}),
                    html.P(
                        "The total elapsed time of selected groups will be ploted here.",
                        className="card-text",
                        style={'font-size': '0.5rem'}
                    ),
                ]
            )
        ],
        color='success',
        inverse=True
    ),
        id="track_plot")

    trending_groups = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.FormGroup(
                            [
                                dbc.Label("From Group"),
                                dcc.Dropdown(id="trend_group_start", placeholder="Select group number ...",
                                             multi=False, disabled=False),
                                dbc.FormText("Input keyword above and select start group."),
                            ],
                            style={'font-size': '0.9rem'}
                        ),
                    ),
                    dbc.Col(
                        dbc.FormGroup(
                            [
                                dbc.Label("To Group"),
                                dcc.Dropdown(id="trend_group_end", placeholder="Select group number ...",
                                             multi=False, disabled=False),
                                dbc.FormText("Input keyword above and select end group."),
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
                                id="switches-inline-input-track",
                                inline=False,
                                switch=True,
                            ),
                        ],
                        style={'font-size': '0.9rem'}
                    ),
                ],
                className='mt-4'
            ),
            dbc.Row(
                [
                    dbc.Button("Start Track", id="search_track", color='success', outline=True, block=True,
                               className='mt-2'),
                ]
            ),

            dbc.Row(
                [
                    dbc.Col(track_plot, className='mt-4')
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
                                dbc.Col(html.Img(src='./assets/img/trending.png', height="35px"),
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
            'background-color': '#4582EC',
        }
    )

    heatmap_matrix = html.Div(id='case_heatmap')

    testplan_area = dbc.Row(
        [
            dbc.Col
                (
                dbc.Jumbotron(
                    [

                        dbc.Row(
                            [
                                dbc.Col(html.Img(src='./assets/img/testplan.png', height="35px"),
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
                        dbc.Row(dbc.Col(heatmap_matrix, width=12)),
                    ],
                    className='mt-2 jumbotron',
                ),
                width=12,
            ),
        ],
        justify="center",
        align="center",
        style={
            'background-color': '#4582EC',
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

    file_upload = html.Div(
        [
            dcc.Upload(
                id='upload-f04',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
        ]
    )

    external_graph = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(html.Div(id='output-f04-upload')),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(html.Div(id='ef04_graph_main'), width=6),
                    dbc.Col(html.Div(id='ef04_graph_nltrd3'), width=6),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(html.Div(id='ef04_table_main'), className='mt-3'),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(html.Div(id='ef04_table_nltrd3'), className='mt-3'),
                ]
            ),
        ],
    )

    toolkit_content0 = dbc.Row(
                [
                    dbc.Col
                    (
                        dbc.Jumbotron(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(html.Img(src='./assets/img/toolkit.png', height="35px"),
                                                width='auto', style={'margin': 'auto'}),
                                        dbc.Col(html.H6("External FO4 File Comparision",
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
                                        dbc.Col(file_upload),
                                    ],
                                    justify="start",
                                    align="center",
                                ),
                                dbc.Row(
                                    [
                                        dbc.FormGroup(
                                            [
                                                dbc.Checklist(
                                                    options=[
                                                        {"label": "List All Modules/Sub-modules", "value": 1},
                                                        {"label": "Print Perf. Table Data", "value": 2},
                                                    ],
                                                    value=[],
                                                    id="external-switch",
                                                    inline=True,
                                                    switch=True,
                                                ),
                                            ],
                                            style={'font-size': '0.9rem'}
                                        ),
                                    ],
                                    justify="start",
                                    align="center",
                                    className='mt-3'
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

    toolkit_content1 = dbc.Row(
                [
                    dbc.Col
                    (
                        dbc.Jumbotron(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(external_graph),
                                    ],
                                    justify="start",
                                    align="center",
                                ),
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

    toolkit_container = html.Div([toolkit_content0, toolkit_content1])

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
                                dbc.Tab(label="Perf-Toolkit", tab_id="Perf-Toolkit", children=toolkit_container,
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
                style={
                    'background-color': '#4582EC'
                },
                className='mt-3'
            )
        ]
    )

    Main_Container = [navbar, main_card]

    return Main_Container

