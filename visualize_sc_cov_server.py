#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 11:40:46 2021

@author: EduardoWork
"""

import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from parse_sc_cov import parse_info
from parse_sc_cov import unpack


df_casos_packed = parse_info('covid_sc_casos.csv')
df_mortes_packed = parse_info('covid_sc_mortes.csv')

df_casos = unpack(df_casos_packed, 'dados')
df_mortes = unpack(df_mortes_packed, 'dados')

app = dash.Dash()

server = app.server

app.layout = html.Div([

    # Dropdown menu
    html.Div([

        html.Div([

            html.Label(['Selecione um município: '],
                       style={'font-weight': 'bold',
                              'fontFamily': 'Helvetica'}
                       ),

        ], style={'text-align': 'center',
                  'width': '15%',
                  'display': 'inline-block'}),

        html.Div([

            dcc.Dropdown(
                id='dropdown',
                options=[{'label': i, 'value': i}
                         for i in sorted(list(df_casos.columns))[:-2]],
                value='Florianopolis',
                multi=False,
                searchable=True,
                clearable=False,
                style={'fontFamily': 'Helvetica'}
                ),

        ], style={'width': '15%',
                  'display': 'inline-block',
                  'verticalAlign': 'middle'}
                  ),

    ], className='dropdown_menu'),

    html.Br(),

    # Gráfico casos total
    html.Div([

        html.Div([
            dcc.Graph(id='graph_casos')
        ], className='two columns'),

    ], className='row', style={'width': '50%', 'display': 'inline-block'}),

    # Gráfico óbitos total
    html.Div([

        html.Div([
            dcc.Graph(id='graph_mortes')
        ], className='two columns'),

    ], className='row', style={'width': '50%', 'display': 'inline-block'}),

    # Gráfico casos novos
    html.Div([

        html.Div([
            dcc.Graph(id='graph_casos_novos')
        ], className='two columns'),

    ], className='row', style={'width': '50%', 'display': 'inline-block'}),

    # Gráfico óbitos novos
    html.Div([

        html.Div([
            dcc.Graph(id='graph_mortes_novos')
        ], className='two columns'),

    ], className='row', style={'width': '50%', 'display': 'inline-block'})
    ])


@app.callback(
    Output(component_id='graph_casos', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')]
    )
def update_graph_casos(dropdown):
    """Atualiza o gráfico Casos confirmados - total."""
    df_copy = df_casos

    chart = px.bar(
        x=df_copy['date'],
        y=df_copy[dropdown])

    chart.update_traces(hovertemplate=
                        '<b> Casos confirmados - total: %{y} </b>' +
                        '<br> %{x} '
                        )

    chart.update_layout(title_text="Casos confirmados - total",
                        title_font_size=18,
                        xaxis_title='',
                        yaxis_title='')

    return chart


@app.callback(
    Output(component_id='graph_mortes', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')]
    )
def update_graph_mortes(dropdown):
    """Atualiza o gráfico Óbitos - total."""
    df_copy = df_mortes

    chart = px.bar(
        x=df_copy['date'],
        y=df_copy[dropdown])

    chart.update_traces(marker_color='tomato',
                        hovertemplate='<b> Óbitos - total: %{y} </b>' +
                                      '<br> %{x} '
                        )

    chart.update_layout(title_text="Óbitos - total",
                        title_font_size=18,
                        xaxis_title='',
                        yaxis_title='')

    return chart


@app.callback(
    Output(component_id='graph_casos_novos', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')]
    )
def update_graph_casos_novos(dropdown):
    """Atualiza o gráfico Casos confirmados - novos."""
    df_copy = df_casos

    casos_novos = []
    casos_dia_anterior = 0

    for date, casos_dia in zip(df_copy.get('date'), df_copy.get(dropdown)):
        try:
            casos_novos.append({'date': date,
                                'casos': int(casos_dia) - casos_dia_anterior})
        except ValueError:
            casos_novos.append({'date': date,
                                'casos': 0 - casos_dia_anterior})
        casos_dia_anterior = casos_dia

    df_casos_novos = pd.DataFrame(casos_novos)

    chart = px.bar(
        x=df_casos_novos['date'],
        y=df_casos_novos['casos'])

    chart.update_traces(hovertemplate='<b> Casos confirmados: %{y} </b>' +
                                      '<br> %{x} '
                        )

    # Média móvel de 7 dias
    df_casos_novos['SMA_7_days'] = df_casos_novos.iloc[:, 1].rolling(window=7).mean()
    chart.add_trace(
        go.Scatter(
            x=df_casos_novos['date'],
            y=df_casos_novos['SMA_7_days'],
            mode='lines',
            line=go.scatter.Line(color='blue'),
            name='Média móvel de 7 dias',
            hovertemplate='<b> %{y} </b>' +
                          '<br> %{x} '
            )
        )

    chart.update_layout(title_text="Casos confirmados - novos",
                        title_font_size=18,
                        legend=dict(yanchor='top',
                                    y=0.99,
                                    xanchor='left',
                                    x=0.01),
                        xaxis_title='',
                        yaxis_title=''
                        )

    return chart


@app.callback(
    Output(component_id='graph_mortes_novos', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')]
    )
def update_graph_mortes_novos(dropdown):
    """Atualiza o gráfico Óbitos - novos."""
    df_copy = df_mortes

    casos_novos = []
    casos_dia_anterior = 0

    for date, casos_dia in zip(df_copy.get('date'), df_copy.get(dropdown)):
        try:
            casos_novos.append({'date': date,
                                'casos': int(casos_dia) - casos_dia_anterior})
        except ValueError:
            casos_novos.append({'date': date,
                                'casos': 0 - casos_dia_anterior})
        casos_dia_anterior = casos_dia

    df_casos_novos = pd.DataFrame(casos_novos)

    chart = px.bar(
        x=df_casos_novos['date'],
        y=df_casos_novos['casos'])

    chart.update_traces(marker_color='tomato',
                        hovertemplate='<b> Óbitos: %{y} </b>' +
                                      '<br> %{x} '
                        )

    # Média móvel de 7 dias
    df_casos_novos['SMA_7_days'] = df_casos_novos.iloc[:, 1].rolling(window=7).mean()
    chart.add_trace(
        go.Scatter(
            x=df_casos_novos['date'],
            y=df_casos_novos['SMA_7_days'],
            mode='lines',
            line=go.scatter.Line(color='red'),
            name='Média móvel de 7 dias',
            hovertemplate='<b> %{y} </b>' +
                          '<br> %{x} '
            )
        )

    chart.update_layout(title_text="Óbitos - novos",
                        title_font_size=18,
                        legend=dict(yanchor='top',
                                    y=0.99,
                                    xanchor='left',
                                    x=0.01),
                        xaxis_title='',
                        yaxis_title=''
                        )

    return chart


if __name__ == '__main__':
    app.run_server(debug=True)
