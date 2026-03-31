# spacex_dash_app.py
# Minimal local version for Tasks 1-4

import pandas as pd
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output

# Read the SpaceX data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
min_payload = int(spacex_df['Payload Mass (kg)'].min())
max_payload = int(spacex_df['Payload Mass (kg)'].max())

# Build dropdown options
unique_sites = sorted(spacex_df['Launch Site'].unique())
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in unique_sites
]

# Simple slider marks (local use)
marks = {0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'}

# Create the Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1 - dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),

    # TASK 2 - pie chart
    dcc.Graph(id='success-pie-chart'),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3 - payload slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks=marks,
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4 - scatter chart
    dcc.Graph(id='success-payload-scatter-chart'),
])

# TASK 2 callback: update pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        df_grouped = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(df_grouped,
                     values='class',
                     names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site].copy()
        df_site['Outcome'] = df_site['class'].map({0: 'Failure', 1: 'Success'})
        df_outcomes = df_site.groupby('Outcome').size().reset_index(name='counts')
        fig = px.pie(df_outcomes,
                     values='counts',
                     names='Outcome',
                     title=f'Success vs Failure for {selected_site}')
    return fig

# TASK 4 callback: update scatter chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)].copy()
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    title = 'Payload vs. Outcome (All Sites)' if selected_site == 'ALL' else f'Payload vs. Outcome ({selected_site})'
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site', 'Payload Mass (kg)'],
        title=title,
        labels={'class': 'Launch Outcome (0 = Failure, 1 = Success)'}
    )
    return fig

if __name__ == '__main__':
    # Prefer app.run (Dash v3+). If that fails (older Dash), fall back to app.run_server.
    try:
        app.run(debug=True)
    except Exception:
        app.run_server(debug=True)