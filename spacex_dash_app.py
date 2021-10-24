# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px


# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Construct pie data
## Success
estados_exitosos = ['Success','Success  (payload status unclear)']
exitos_pie_df = spacex_df[spacex_df['Mission Outcome'].isin(estados_exitosos)]
exitos_pie_df = exitos_pie_df.groupby('Launch Site')[['Mission Outcome']].count()
exitos_pie_df.columns = ['Exitos']
exitos_pie_df = exitos_pie_df.reset_index()

## Data by launch site
pie_df = spacex_df.groupby(by=['Launch Site','Mission Outcome'])[['Mission Outcome']].count()
pie_df.columns=['Cuenta']
#pie_df = pie_df.reset_index()

# Launch Sites
launch_sites = spacex_df['Launch Site'].unique()
launch_sites = ['All'] + list(launch_sites) 

# Create a dash application
app = dash.Dash(__name__)
#app.config.suppress_callback_exceptions = True

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                # Add an division
                                html.Div([
                    
                                    html.Div(
                                        [
                                            html.H2('Select site:', style={
                                                'margin-right': '2em'}),
                                        ]
                                    ),
                                    
                                    dcc.Dropdown(id='site-dropdown',
                                                options=[
                                                    {'label': i, 'value': i} for i in launch_sites],
                                                value='All',
                                                placeholder='Select a site', 
                                                style={'width': '80%', 'padding': '3px', 'font-size': '20px',
                                                        'text-align-last': 'center'})
                                ], style={'display': 'flex'}),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', min=min_payload, max=max_payload, step=None, dots=True,
                                                marks={0:'0', 1000:'1000', 2000:'2000', 3000:'3000', 4000:'4000', 5000:'5000',
                                                       6000:'6000', 7000:'7000', 8000:'8000', 9000:'9000', 
                                                       max_payload:str(max_payload)},
                                                value=[0, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output('success-pie-chart', 'figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_graph(site_value):
    if site_value=='All':
        pie_fig = px.pie(exitos_pie_df, values='Exitos', names='Launch Site',
                         title='% Mission Outcome')
    else:
        fig_data = pie_df.loc[site_value]
        fig_data = fig_data.reset_index()
        pie_fig = px.pie(fig_data, values='Cuenta', names='Mission Outcome',
                         title='% Mission Outcome')
    return pie_fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output('success-payload-scatter-chart', 'figure'),
              Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value'),
              )
def get_scatterplot(site, payload):
    if site=='All':
        query = '`Payload Mass (kg)` >= {0} and `Payload Mass (kg)` <= {1}'.format(payload[0], payload[1])
        data_scatter = spacex_df.query(query)
        scatter_fig = px.scatter(data_scatter, x='Payload Mass (kg)', y='Launch Site', color='Booster Version') #color='Mission Outcome')
        return scatter_fig
    else:
        query = '`Payload Mass (kg)` >= {0} and `Payload Mass (kg)` <= {1} and `Launch Site` == "{2}"'.format(
            payload[0], payload[1], site)
        data_scatter = spacex_df.query(query)
        scatter_fig = px.scatter(data_scatter, x='Payload Mass (kg)', y='Launch Site',  color='Booster Version') #color='Mission Outcome')
        return scatter_fig
# Run the app
if __name__ == '__main__':
    app.run_server()
