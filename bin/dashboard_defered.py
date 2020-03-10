import var_init
var_init.setenvvars()

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import database_set
import plotly.graph_objs as go

table = database_set.DatabaseTable('RUN_1')

key = table.db_read_init()

a = table.db_distinct('Plan', 'GROUP')
b = table.db_distinct('Plan', 'CASE')

print_out = table.KeySet.select().where(table.KeySet.name == 'key_result')[0].key.split(',')

print(print_out)

print_out1 = ['NLTRD3', 'EMG', 'EMA', 'ELAPSED']

print_out2 = ['NLEMG2', 'SPDC', 'NL2QNV2', 'NLTRD3']


def dataframe_conv(vk, pk=print_out):

    data = {}

    for i in range(len(pk)):

        dc = []

        for j in range(len(vk)):

            dc.append(vk[j][i])

        data[pk[i]] = dc

    df = pd.DataFrame(data)

    return df


def generate_table(dataframe, max_rows=100):

    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


def onLoad_division_options(distinct):

    division_options = (
        [{'label': str.strip(division), 'value': str.strip(division)}
         for division in distinct]
    )
    return division_options


external_stylesheets = ['https://codepen.io/haoran_ju/pen/ZEGOWjV.css']

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[

    html.Div([

        html.H4(children='Nastran Performance Test Result'),

    ], className='twelve columns', style = {
            'margin-left':'100px',
            'align':'center',
            }),

    html.Div([

        html.Div([
            html.Div('Select Group:', className='two columns'),
            html.Div(dcc.Dropdown(id='division-selector0',
                                  options=onLoad_division_options(a),
                                  value=['1899.116'],
                                  multi=True),
                     className='twelve columns')
        ], className='five columns'),

        html.Div([
            html.Div('Select Model:', className='two columns'),
            html.Div(dcc.Dropdown(id='division-selector1',
                                  options=onLoad_division_options(b),
                                  value=['hexa0', 'hexa1', 'hexa2'],
                                  multi=True),
                     className='twelve columns')
        ], className='five columns'),

    ], className='ten columns'),

    html.Div([

        html.Div(id='table_case', className='five columns'),

        html.Div(id='table', className='five columns'),

    ], className='ten columns', style = {
            'font':'160%',
            }),

    dcc.Graph(id='compare-graph', className='five columns', style = {
            'margin-left':'-10px',
            'margin-top':'50px',
            'align':'left',
            }),

    dcc.Graph(id='compare-graph1', className='five columns', style = {
            'margin-left':'-10px',
            'margin-top':'50px',
            'align':'left',
            }),

], className='twelve columns')

'''
@app.callback(
    Output(component_id='division-selector1', component_property='options'),
    [
        Input(component_id='division-selector0', component_property='value'),

    ]
)
def populate_combine_selector(division0):

    search_all = []

    search1 = []

    for value in division0:

        search1.append(['GROUP', value])

    search_all = [search1]

    vk = table.db_read_filter('Plan', search_key=search_all, print_key=['CASE'])

    print(vk)

    return [
        {'label': i[0], 'value': i[0]}
        for i in vk
    ]
'''
@app.callback(
    Output(component_id='table_case', component_property='children'),
    [
        Input(component_id='division-selector0', component_property='value'),
        Input(component_id='division-selector1', component_property='value'),
    ]
)
def populate_case_selector(division0, division1):

    search_all = []

    search1 = []

    for value in division0:

        search1.append(['GROUP', value])

    search2 = []

    for value in division1:

        search2.append(['CASE', value])

    search_all = [search2]

    vk = table.db_read_filter('Case', search_key=search_all, print_key=['CASE', 'SMP', 'LGSTRN', 'KUPDATE', 'SOLVER'])

    df = dataframe_conv(vk, ['CASE', 'SMP', 'LGSTRN', 'KUPDATE', 'SOLVER'])

    table_html = generate_table(df)

    return table_html

@app.callback(
    Output(component_id='table', component_property='children'),
    [
        Input(component_id='division-selector0', component_property='value'),
        Input(component_id='division-selector1', component_property='value'),
    ]
)
def populate_season_selector(division0, division1):

    search_all = []

    search1 = []

    for value in division0:

        search1.append(['GROUP', value])

    search2 = []

    for value in division1:

        search2.append(['CASE', value])

    search_all = [search1, search2]

    vk = table.db_read_filter('Plan', search_key=search_all, print_key=['RESULT'])

    vk11 = table.db_read_filter('Plan', search_key=search_all, print_key=['GROUP'])

    vk12 = table.db_read_filter('Case', search_key=[search2], print_key=['SMP'])

    smp = vk12

    search_i = []

    for i in vk:

        search_i.append(['RESULT', i[0]])

    vk1 = table.db_read_filter('Result', search_key=[search_i], print_key= print_out2 + print_out1)

    df = dataframe_conv(vk1, print_out2 + print_out1)

    df1 = dataframe_conv(vk11, ['GROUP'])

    a = pd.concat([df1, df], axis=1)

    table_html = generate_table(a)

    return table_html

@app.callback(
    Output(component_id='compare-graph', component_property='figure'),
    [
        Input(component_id='division-selector0', component_property='value'),
        Input(component_id='division-selector1', component_property='value'),
    ]
)
def update_graph(division0, division1):
    search_all = []

    search1 = []

    for value in division0:

        search1.append(['GROUP', value])

    search2 = []

    for value in division1:

        search2.append(['CASE', value])

    search_all = [search1, search2]

    vk = table.db_read_filter('Plan', search_key=search_all, print_key=['RESULT'])

    search_i = []

    for i in vk:

        search_i.append(['RESULT', i[0]])

    vk1 = table.db_read_filter('Result', search_key=[search_i], print_key=print_out1)

    vk12 = table.db_read_filter('Case', search_key=[search2], print_key=['SMP'])

    smp = vk12

    df = dataframe_conv(vk1, print_out1)

    name = df[list(df.keys())[1]]

    pv = df[list(df.keys())]

    trace = []

    for i in range(pv.shape[0]):

        trace.append(go.Bar(x=list(pv.keys()), y=pv.loc[i], name=str(name.loc[i])))

    return {
        'data': trace,
        'layout':
        go.Layout(
            title='Total Module Elapsed Time')
    }


@app.callback(
    Output(component_id='compare-graph1', component_property='figure'),
    [
        Input(component_id='division-selector0', component_property='value'),
        Input(component_id='division-selector1', component_property='value'),
    ]
)
def update_graph1(division0, division1):
    search_all = []

    search1 = []

    for value in division0:

        search1.append(['GROUP', value])

    search2 = []

    for value in division1:

        search2.append(['CASE', value])

    search_all = [search1, search2]

    vk = table.db_read_filter('Plan', search_key=search_all, print_key=['RESULT'])

    search_i = []

    for i in vk:

        search_i.append(['RESULT', i[0]])

    vk1 = table.db_read_filter('Result', search_key=[search_i], print_key=print_out2)

    vk12 = table.db_read_filter('Case', search_key=[search2], print_key=['SMP'])

    smp = vk12

    df = dataframe_conv(vk1, print_out2)

    name = df[list(df.keys())[1]]

    pv = df[list(df.keys())]

    trace = []

    for i in range(pv.shape[0]):

        trace.append(go.Bar(x=list(pv.keys()), y=pv.loc[i], name=str(name.loc[i])))

    return {
        'data': trace,
        'layout':
        go.Layout(
            title='NLTRD3 Submodule Elapsed Time')
    }


if __name__ == '__main__':

    app.run_server(debug=True)
    
    #app.run_server(host='0.0.0.0')