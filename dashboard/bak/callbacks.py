from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from layouts import *
from app import app
import globalvar as gl
import datetime
import os
import pandas as pd
import time
import uuid
from flask_caching import Cache

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
    'CACHE_THRESHOLD': 200
})

# add callback for toggling the collapse on small screens

cnames = ['#00BFFF', '#00008B', '#008B8B', '#B8860B', '#006400', '#BDB76B', '#FF8C00', '#8B0000',
                       '#8FBC8F', '#9400D3']


def get_dataframe(session_id):

    @cache.memoize()
    def query_and_serialize_data(session_id):

        df1 = gl.get_value('dfpl')
        df2 = gl.get_value('dfcs')
        df3 = gl.get_value('dfmn')
        df4 = gl.get_value('dfnl3')

        df = df1.copy()

        group_sorted = df.sort_values(by="GROUP", ascending=False)

        latest_group = group_sorted.max().GROUP

        baseline_group = group_sorted.min().GROUP

        prev_group = group_sorted.loc[group_sorted['GROUP'] < latest_group].GROUP[0]

        latest_case_number = df.loc[df['GROUP'] == latest_group].shape[0]

        return {'PLAN': df1.to_json(), 'CASE': df2.to_json(), 'MAIN': df3.to_json(), 'NLTRD3': df4.to_json()}

    k = query_and_serialize_data(session_id)

    print(k)

    return pd.read_json(query_and_serialize_data(session_id))


def Hex_to_RGB(hex):

    r = int(hex[1:3], 16)
    g = int(hex[3:5], 16)
    b = int(hex[5:7], 16)
    rgb = str(r) + ',' + str(g) + ',' + str(b)
    return rgb


def layout_update():

    layout_generator = LayoutUpdate('baseline')

    main_container = layout_generator.container_generator()

    session_id = str(uuid.uuid4())

    return html.Div([
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        html.Div(main_container),
        html.Button('Get data', id='get-data-button'),
        html.Div(id='output-1'),
    ])


@app.callback(Output('output-1', 'children'),
              [Input('get-data-button', 'n_clicks'),
               Input('session-id', 'children')])
def display_value_1(value, session_id):
    df = get_dataframe(session_id)
    return html.Div([
        'Output 1 - Button has been clicked {} times'.format(value),
        html.Pre(df.to_csv())
    ])


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


def create_time_series(curve, colors):

    fig = go.Figure()

    index = 0

    for ckey in curve.keys():

        if len(curve[ckey]) > 1:

            sk = sorted(curve[ckey].keys())

            x_list = sk

            y_list = []

            for i in x_list:

                y_list.append(curve[ckey][i])

            fig.add_trace(
                go.Scatter(
                    x=x_list,
                    y=y_list,
                    name=ckey,
                    mode='lines+markers',
                    line=dict(color='rgba(' + Hex_to_RGB(colors[index]) + ', 0.5)', width=4),
                    marker=dict(color=colors[index], size=10, opacity=0.5,
                                line=dict(color='MediumPurple', width=2)
            ))),

        index = index + 1

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

    return dcc.Graph(id='histroy_elapsed', figure=fig)


@app.callback(
    Output('vision_box', "children"),
    [Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "derived_virtual_selected_rows")])
def update_graphs(rows, derived_virtual_selected_rows):

    if derived_virtual_selected_rows is None:

        derived_virtual_selected_rows = []

    curve = {}

    colors = []

    try:

        dff = df if rows is None else pd.DataFrame(rows)

        multi_factor = 1

        for i in range(len(dff)):

            index = (i // len(cnames))

            kp = i - len(cnames)*index

            colors.append(cnames[kp])

        #colors = ['#f0ad4e' if i in derived_virtual_selected_rows else '#4582EC' for i in range(len(dff))]

        group = dff.groupby('CASE').groups

        for i in range(len(dff)):

            group_elapsed = {}

            for item in group[dff.loc[i, 'CASE']]:

                group_elapsed[dff.loc[item, 'GROUP']] = dff.loc[item, 'ELAPSED']

            curve[dff.loc[i, 'CASE']] = group_elapsed

    except:

        pass

    return create_time_series(curve, colors)

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
    [Input("group-multi-dynamic-dropdown", "value"),
     Input('session-id', 'children')],
)
def update_single_options(group_value, session_id):

    dfcl = gl.get_value("dfpl").copy()

    dfcl = get_dataframe(session_id)

    group_key_list = gl.get_value('group_key')

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

    dfpl = gl.get_value('dfpl').copy()

    dfmn = gl.get_value('dfmn').copy()

    fig = go.Figure()

    default = html.Div(dbc.Card(
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

            print(x_list)

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

    dfpl = gl.get_value('dfpl').copy()

    dfmn = gl.get_value('dfnl3').copy()

    fig = go.Figure()

    default = html.Div(dbc.Card(
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

    dfpl = gl.get_value('dfpl').copy()

    dfmn = gl.get_value('dfmn').copy()

    dfnl3 = gl.get_value('dfnl3').copy()

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
    [Input("group_range", "value")],
)
def add_range_group(range_group):

    groups = gl.get_value('total_groups')

    return groups[range_group[0]], groups[range_group[1]]

'''
@app.callback(
    Output("group_range", "value"),
    [Input("trend_group_start", "value"),
     Input("trend_group_end", "value")],
)
def update_trend_group(start_value, end_value):

    groups = gl.get_value('total_groups')

    start_index = groups.index(start_value)

    end_index = groups.index(end_value)

    return [start_index, end_index]

'''