import pandas as pd
import json
from urllib.request import urlopen
import plotly.graph_objects as go
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output

# Load geojson for provinces
with urlopen("https://raw.githubusercontent.com/chingchai/OpenGISData-Thailand/master/provinces.geojson") as response:
    provinces = json.load(response)

# Load data for student numbers
with urlopen("https://gpa.obec.go.th/reportdata/pp3-4_2566_province.json") as response:
    data = json.load(response)
    df = pd.DataFrame(data)

# Initialize the Dash app
app = Dash(__name__)

# Define the layout
app.layout = html.Div([
    # Navigation bar
    html.Nav([
        html.Div("Graduated M6 Student 2566 Dashboard", style={'fontSize': 24, 'padding': '10px'}),
        html.Div([
            dcc.Dropdown(
                id='province-dropdown',
                options=[{'label': prov, 'value': prov} for prov in df.schools_province.unique()],
                value=[],
                multi=True,
                style={'width': '300px'}
            )
        ], style={'marginLeft': 'auto', 'padding': '10px'}),
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'backgroundColor': '#f8f9fa',
        'borderBottom': '1px solid #ddd'
    }),
    
    html.Div([
        html.Div([
            # Map
            dcc.Graph(
                id='choropleth-map',
                config={'scrollZoom': True},
                style={'width': '100%', 'height': 'calc(100vh - 100px)'}  # Adjust height accordingly
            ),
        ], style={'flex': 1, 'padding': '10px'}),
        html.Div([
            dcc.Graph(
                id='bar-chart',
                style={'width': '100%', 'height': '50%'}  # Adjust height as needed
            ),
            # Data Table
            dash_table.DataTable(
                id='data-table',
                columns=[
                    {"name": "Province", "id": "schools_province"},
                    {"name": "Total Male", "id": "totalmale"},
                    {"name": "Total Female", "id": "totalfemale"},
                    {"name": "Total Students", "id": "totalstd"}
                ],
                data=[],  # Initialize with empty data
                page_size=10,  # Number of rows per page
                page_current=0,  # Start with the first page
                style_cell={'textAlign': 'left'},
            )
            # Bar Chart
            
        ], style={'flex': 1, 'padding': '10px'})
    ], style={"display": "flex", "flexDirection": "row", 'width': "100%", 'padding': '10px 0 10px 0'})
])

# Define the callback to update the map, table, and bar chart
@app.callback(
    [Output('choropleth-map', 'figure'),
     Output('data-table', 'data'),
     Output('bar-chart', 'figure'),
     Output('province-dropdown', 'value')],
    [Input('province-dropdown', 'value')]
)
def update_content(selected_provinces):
    # Handle dropdown and click event

    if selected_provinces:
        filtered_df = df[df['schools_province'].isin(selected_provinces)]
    else:
        filtered_df = df

    # Create the choropleth map figure
    fig_map = go.Figure(go.Choroplethmapbox(
        geojson=provinces, 
        locations=df.schools_province, 
        z=df.totalstd, 
        featureidkey="properties.pro_th",
        colorscale='Inferno',  # Default color scale
        marker_opacity=0.5, 
        marker_line_width=0.5
    ))

    fig_map.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=5.15,  # Zoom level
        mapbox_center={"lat": 13.1111, "lon": 100.9390},  # Center of Thailand
        margin={"r":0,"t":0,"l":0,"b":0},
    )

    # Create the bar chart figure
    fig_bar = go.Figure()
    if not filtered_df.empty:
        # Sort the data by 'totalstd'
        sorted_df = filtered_df.sort_values(by='totalstd')
        
        fig_bar.add_trace(go.Bar(
            x=sorted_df['schools_province'],
            y=sorted_df['totalstd'],
            marker_color='lightsalmon'
        ))

    fig_bar.update_layout(
        title='Total Students per Province',
        xaxis_title='Province',
        yaxis_title='Total Students',
        yaxis=dict(
            autorange=True,  # Ensure y-axis is automatically ranged from lowest to highest value
            type='linear'
        ),
        margin={"r":0,"t":50,"l":0,"b":0}
    )

    # Update table data based on selected provinces
    table_data = filtered_df.to_dict('records')

    return fig_map, table_data, fig_bar, selected_provinces

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)
