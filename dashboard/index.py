import sys

sys.path.append('../bin/')

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from layouts_local import *
import callbacks

import datetime

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


app.layout = callbacks.layout_update


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