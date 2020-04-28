import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import numpy as np
import plotly.graph_objs as go



data = pd.read_csv('data\price_RSV2.csv')
del data['Unnamed: 0']
data['StationCode'] = data['GTPName'].apply(lambda s: s[0:6])
data['TG'] = np.select(
    [data['TG'] == 0, 
    data['TG'] != 0],
    [.0001, data['TG']])
data['RSV_Price'] = np.select([data['RSV_Price'] == 0, data['RSV_Price'] != 0],[data['AVG_Price'], data['RSV_Price']])
data['Cost'] = data['TG'] * data['RSV_Price']

data_d = data.groupby(['StationCode', 'Year', 'Month', 'Day', 'Hour'], as_index=False)['TG', 'Cost'].apply(np.sum).reset_index()
data_d['Price'] = (data_d['Cost'] / data_d['TG']).round(2)

data_d_ad = data_d[(data_d['StationCode'] == 'GADLER') & (data_d['Day'] == 1)]

trace_ad = go.Scatter(x=list(data_d_ad['Hour']),
                      y=list(data_d_ad['Price']),
                      line=dict(color='#1B1BEB'))

dic_station = {
    'GKIRGR': 'Киришская ГРЭС',
    'GVOLOG': 'Череповецская ГРЭС',
    'GPSKOG': 'Псковская ГРЭС',
    'GRYAZG': 'Рязанская ГРЭС',
    'GNCHEG': 'Новочеркасская ГРЭС',
    'GSTAGR': 'Ставропольская ГРЭС',
    'GADLER': 'Адлерская ТЭС',
    'GCHECH': 'Грозненская ТЭС',
    'GSVERD': 'Серовская ГРЭС',
    'GTROIG': 'Троицкая ГРЭС',
    'GTUMEN': 'Сургутская ГРЭС',
    'GKRASG': 'Красноярская ГРЭС-2'
    }

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    html.Div([
        html.H2('Цена РСВ'),
        html.Img(src='/assets/Logo OGK-2.png')
    ], className='banner'),
    html.Div([
        html.Div([
            dcc.Checklist(
                id='list_station',
                options=[
                    {'label': 'Киришская ГРЭС', 'value': 'GKIRGR'},
                    {'label': 'Череповецская ГРЭС', 'value': 'GVOLOG'},
                    {'label': 'Псковская ГРЭС', 'value': 'GPSKOG'},
                    {'label': 'Рязанская ГРЭС', 'value': 'GRYAZG'},
                    {'label': 'Новочеркасская ГРЭС', 'value': 'GNCHEG'},
                    {'label': 'Ставропольска ГРЭС', 'value': 'GSTAGR'},
                    {'label': 'Адлерская ТЭС', 'value': 'GADLER'},
                    {'label': 'Грозненская ТЭС', 'value': 'GCHECH'},
                    {'label': 'Серовская ГРЭС', 'value': 'GSVERD'},
                    {'label': 'Троицкая ГРЭС', 'value': 'GTROIG'},
                    {'label': 'Сургутская ГРЭС', 'value': 'GTUMEN'},
                    {'label': 'Красноярская ГРЭС-2', 'value': 'GKRASG'}
                ],
                value=['GKIRGR']
            ),
        ], className='two columns'),

        html.Div([
            dcc.Graph(
                id='graph_rsv_hours',
                figure={
                    'data': [trace_ad]
                }
            )

        ], className='six columns'),

    ], className={'columnCount': 2})
])

@app.callback(
    Output('graph_rsv_hours', 'figure'),
    [Input('list_station', 'value')]
)

def updet_figure(station):
    tracers = []
    for i in np.array(station):
        tracers.append(
            dict(
                x = data_d[(data_d['StationCode'] == i) & (data_d['Day'] == 1)]['Hour'],
                y = data_d[(data_d['StationCode'] == i) & (data_d['Day'] == 1)]['Price'],
                mode='lines',
                line=dict(shape="spline", smoothing=2, width=3),
                name=dic_station[i]
            )
        )

    return {
        'data': tracers,
        'layout': dict(
            xaxis={'title': 'Часы'},
            yaxis={'title': 'Цена РСВ'}
        )
    }


if __name__ == '__main__':
    app.run_server(debug=False)