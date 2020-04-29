

import dash
import dash_core_components as dcc
import dash_html_components as html
#put in a separate module all part with pandas and numpy
#rewrite with clear names
import pandas as pd
from dash.dependencies import Input, Output
import numpy as np
import plotly.graph_objs as go

data = pd.read_csv('./data/price_RSV2.CSV')
del data['Unnamed: 0']
data['StationCode'] = data['GTPName'].apply(lambda s: s[0:6])
data['TG'] = np.select([data['TG'] == 0, data['TG'] != 0],[.0001, data['TG']])
data['RSV_Price'] = np.select([data['RSV_Price'] == 0, data['RSV_Price'] != 0],[data['AVG_Price'], data['RSV_Price']])
data['Cost'] = data['TG'] * data['RSV_Price']

data_d = data.groupby(['StationCode', 'Year', 'Month', 'Day', 'Hour'], as_index=False)['TG', 'Cost'].apply(np.sum).reset_index()
data_d['Price'] = (data_d['Cost'] / data_d['TG']).round(2)

data_m = data.groupby(['StationCode', 'Year', 'Month', 'Day'], as_index=False)['TG', 'Cost'].apply(np.sum).reset_index()
data_m['Price'] = (data_m['Cost'] / data_m['TG']).round(2)

data_m_ad = data_m[data_m['StationCode'] == 'GADLER']

trace_ad = go.Scatter(x=list(data_m_ad['Day']),
                      y=list(data_m_ad['Price']),
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

server = app.server

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
                value=['GKIRGR', 'GVOLOG', 'GPSKOG', 'GRYAZG', 'GNCHEG', 'GSTAGR', 'GADLER', 'GCHECH', 'GSVERD', 'GTROIG', 'GTUMEN', 'GKRASG']
            ),
        ], className='pretty_container four columns'),

        html.Div([
            html.Div([
                html.H6('Цена на электроэнергию по суткам')
            ]),
            html.Div([
                dcc.Graph(
                    id='graph_rsv_days'
                )
            ]),
            html.Div([
                dcc.Slider(
                    id='days-slider',
                    min=data_m['Day'].min(),
                    max=data_m['Day'].max(),
                    value=data_m['Day'].max(),
                    marks={str(days): str(days) for days in data_m['Day'].unique()}
                ),
                html.Label('Выбор суток')
            ], className='slider'),
            html.Div([
                html.H6('Цена на электроэнергию по часам')
            ]),
            html.Div([
                dcc.Graph(
                    id='graph_rsv_hours'
                )
            ])
        ], className='pretty_container eight columns'),

    ], className={'columnCount': 2})
])

#Построение графика по суткам
@app.callback(
    Output('graph_rsv_days', 'figure'),
    [Input('list_station', 'value')]
)

def updet_figure(station):
    station_day = []
    for i in np.array(station):
        station_day.append(
            dict(
                x = data_m[data_m['StationCode'] == i]['Day'],
                y = data_m[data_m['StationCode'] == i]['Price'],
                mode='lines+markers',
                line=dict(width=3),
                name=dic_station[i]
            )
        )

    return {
        'data': station_day,
        'layout': dict(
            xaxis=dict(showgrid=True,
                       showticklabels=False,
                       showline=True, linewidth=2, linecolor='black',
                       range=[1, data_m['Day'].max()], nticks=data_m['Day'].max()
                       ),
            yaxis=dict(title='Цена РСВ',
                       showgrid=True,
                       showline=True, linewidth=2, linecolor='black'
                       ),
            margin={'l': 82, 'b': 0, 't': 5, 'r': 25},
            legend={'x': 0, 'y': 1.15, 'orientation': 'h', 'yanchor': 'top'},
        )
    }

#Построение графика по часам
@app.callback(
    Output('graph_rsv_hours', 'figure'),
    [Input('list_station', 'value'),
     Input('days-slider', 'value')]
)

def updet_figure(station, days):
    station_hours = []
    for i in np.array(station):
        station_hours.append(
            dict(
                x = data_d[(data_d['StationCode'] == i) & (data_d['Day'] == days)]['Hour'],
                y = data_d[(data_d['StationCode'] == i) & (data_d['Day'] == days)]['Price'],
                mode='lines',
                line=dict(shape="spline", smoothing=2, width=3),
                name=dic_station[i]
            )
        )

    return {
        'data': station_hours,
        'layout': dict(
            xaxis=dict(title='Часы',
                       showgrid=True,
                       howline=True, linewidth=2, linecolor='black',
                       range=[0, 23], nticks=24
                       ),
            yaxis=dict(title='Цена РСВ',
                       showgrid=True,
                       showline=True, linewidth=2, linecolor='black'
                       ),
            margin={'l': 80, 'b': 40, 't': 5, 'r': 10},
            legend={'x': 0, 'y': 1.15, 'orientation': 'h', 'yanchor': 'top'},
        )
    }


if __name__ == '__main__':
    app.run_server(debug=False)