# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the launch data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create app
app = dash.Dash(__name__)
app.title = "SpaceX Launch Records Dashboard"

# ----- Layout -----
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    # TASK 1: Launch site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=([{'label': 'All Sites', 'value': 'ALL'}] +
                 [{'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())]),
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Payload range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# ----- Callbacks -----

# TASK 2: pie chart based on dropdown
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(entered_site):
    if entered_site == 'ALL':
        # count successes per site
        d = (spacex_df[spacex_df['class'] == 1]
             .groupby('Launch Site', as_index=False)['class'].count()
             .rename(columns={'class': 'Successes'}))
        fig = px.pie(d, names='Launch Site', values='Successes',
                     title='Total Successful Launches by Site')
    else:
        d = spacex_df[spacex_df['Launch Site'] == entered_site]['class'].map({1: 'Success', 0: 'Failure'}).value_counts()
        d = d.rename_axis('Outcome').reset_index(name='Count')
        fig = px.pie(d, names='Outcome', values='Count',
                     title=f'Total Success vs Failure for site {entered_site}')
    fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate='%{label}: %{value}')
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig

# TASK 4: scatter chart based on dropdown + slider
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(entered_site, payload_range):
    low, high = payload_range
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                   (spacex_df['Payload Mass (kg)'] <= high)]
    if entered_site != 'ALL':
        df = df[df['Launch Site'] == entered_site]

    fig = px.scatter(
        df, x='Payload Mass (kg)', y='class',
        color='Booster Version Category',
        symbol='Booster Version Category',
        hover_data=['Launch Site'],
        title=('Correlation between Payload and Success for all sites'
               if entered_site == 'ALL' else
               f'Correlation between Payload and Success for {entered_site}')
    )
    fig.update_yaxes(tickmode='array', tickvals=[0, 1], ticktext=['Failure', 'Success'], range=[-0.2, 1.2])
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)  # Skills Network friendly


