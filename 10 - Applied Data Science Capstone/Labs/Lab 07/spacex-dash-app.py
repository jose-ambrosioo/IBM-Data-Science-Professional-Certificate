# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the spacex data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    html.Div(dcc.Dropdown(id='site-dropdown',
                          options=[
                              {'label': 'All Sites', 'value': 'ALL'}] +
                              [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                          value='ALL',
                          placeholder="Select a Launch Site here",
                          searchable=True
                          )),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    html.Div(dcc.RangeSlider(id='payload-slider',
                             min=0, max=10000, step=1000,
                             marks={i: str(i) for i in range(0, 10001, 1000)},
                             value=[min_payload, max_payload]
                             )),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# ----------------------------------------------------------------------
# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Data for all sites: plot overall success (class=1) vs. failure (class=0)
        # We group by the 'class' column and count them
        data = spacex_df['class'].value_counts().reset_index()
        data.columns = ['class', 'count']
        
        fig = px.pie(data, 
                     values='count', 
                     names=['Failure', 'Success'],
                     title='Total Successful vs. Failed Launches for All Sites')
        return fig
    else:
        # Filter data for the specific site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count success (1) vs failure (0) for the selected site
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'count']
        
        # Ensure 'Failure' (0) and 'Success' (1) names are correct
        class_names = {0: 'Failure', 1: 'Success'}
        class_counts['name'] = class_counts['class'].map(class_names)
        
        fig = px.pie(class_counts, 
                     values='count', 
                     names='name',
                     title=f'Launch Success Rate for Site: {entered_site}')
        return fig

# ----------------------------------------------------------------------
# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    
    # Filter data based on the selected payload range
    range_filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                                  (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site == 'ALL':
        # Scatter plot for all sites within the selected payload range
        fig = px.scatter(range_filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         title='Payload vs. Launch Outcome for All Sites')
        return fig
    else:
        # Filter the payload-filtered data by the selected site
        site_payload_filtered_df = range_filtered_df[range_filtered_df['Launch Site'] == entered_site]
        
        # Scatter plot for the specific site and payload range
        fig = px.scatter(site_payload_filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         title=f'Payload vs. Launch Outcome for Site: {entered_site}')
        return fig

# ----------------------------------------------------------------------
# Run the app
if __name__ == '__main__':
    app.run(debug=True)