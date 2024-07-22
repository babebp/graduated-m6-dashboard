import pandas as pd
import json
from urllib.request import urlopen
import plotly.graph_objects as go
import plotly.colors
from dash import Dash, dcc, html, dash_table, ctx
from dash.dependencies import Input, Output, State

# Load geojson for provinces
with urlopen("https://raw.githubusercontent.com/chingchai/OpenGISData-Thailand/master/provinces.geojson") as response:
    provinces = json.load(response)

# Load data for student numbers
with urlopen("https://gpa.obec.go.th/reportdata/pp3-4_2566_province.json") as response:
    data = json.load(response)
    df = pd.DataFrame(data)

# Ensure 'totalstd' is numeric
df['totalstd'] = pd.to_numeric(df['totalstd'], errors='coerce')

# Initialize the Dash app
app = Dash(__name__)

# Define the layout
app.layout = html.Div([
    # Hidden store to manage selected provinces
    dcc.Store(id='selected-provinces-store', data=[]),
    
    # Navigation bar
    html.Nav([
        html.Div("Graduated M6 Student 2566 Dashboard", style={'fontSize': 24, 'padding': '10px'}),
        html.Div([
            dcc.Dropdown(
                id='province-dropdown',
                options=[{'label': prov, 'value': prov} for prov in df.schools_province.unique()],
                value=[],  # Default empty selection
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
                style={'width': '100%', 'height': 'calc(100vh - 120px)'},
                clickData=None  # Initialize with None
            ),
        ], style={'flex': 1, 'padding': '10px'}),
        html.Div([
            dcc.Graph(
                id='bar-chart',
                style={'width': '100%', 'height': '50%'}
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
        ], style={'flex': 1, 'padding': '10px'})
    ], style={"display": "flex", "flexDirection": "row", 'width': "100%", 'padding': '10px 0'})
])

# Define the callback to update the map, table, bar chart, and dropdown
@app.callback(
    [Output('choropleth-map', 'figure'),
     Output('data-table', 'data'),
     Output('bar-chart', 'figure'),
     Output('province-dropdown', 'value'),
     Output('selected-provinces-store', 'data')],
    [Input('province-dropdown', 'value'),
     Input('data-table', 'page_current'),
     Input('choropleth-map', 'clickData')],
    [State('data-table', 'page_size'),
     State('selected-provinces-store', 'data')]
)
def update_content(dropdown_values, page_current, clickData, page_size, stored_provinces):
    # Initialize selected_provinces with stored value
    selected_provinces = stored_provinces or []

    # Handle map click interaction
    if clickData:
        clicked_province = clickData['points'][0]['location']
        if clicked_province in selected_provinces:
            selected_provinces.remove(clicked_province)
        else:
            selected_provinces.append(clicked_province)
    
    # Ensure no duplicates in selected_provinces
    selected_provinces = list(set(selected_provinces))

    # Handle dropdown updates
    if ctx.triggered_id == 'province-dropdown':
        selected_provinces = dropdown_values or []

    # Filter data based on selected provinces
    filtered_df = df[df['schools_province'].isin(selected_provinces)] if selected_provinces else df

    # Define the color scale to be used in both the map and the bar chart
    color_scale = plotly.colors.get_colorscale('Inferno')
    min_std = df['totalstd'].min()
    max_std = df['totalstd'].max()

    # Create the choropleth map figure
    fig_map = go.Figure()

    # Add all provinces with a default color
    fig_map.add_trace(go.Choroplethmapbox(
        geojson=provinces,
        locations=df['schools_province'],
        z=df['totalstd'],
        featureidkey="properties.pro_th",
        colorscale=color_scale,
        colorbar=dict(title='Total Students'),
        marker_opacity=0.5,
        marker_line_width=0.5,
        showscale=True
    ))

    # Highlight selected provinces
    if selected_provinces:
        selected_provinces_geojson = {
            "type": "FeatureCollection",
            "features": [feature for feature in provinces['features'] if feature['properties']['pro_th'] in selected_provinces]
        }

        fig_map.add_trace(go.Choroplethmapbox(
            geojson=selected_provinces_geojson,
            locations=[feature['properties']['pro_th'] for feature in selected_provinces_geojson['features']],
            z=[1] * len(selected_provinces),
            featureidkey="properties.pro_th",
            colorscale=[[0, 'rgba(255,0,0,0.7)'], [1, 'rgba(255,0,0,0.7)']],
            marker_opacity=0.7,
            marker_line_width=2,
            marker_line_color='DarkRed',
            showscale=False
        ))

    fig_map.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=5.15,
        mapbox_center={"lat": 13.1111, "lon": 100.9390},
        margin={"r":0,"t":0,"l":0,"b":0},
    )

    # Create the bar chart figure
    fig_bar = go.Figure()

    if selected_provinces:
        if not filtered_df.empty:
            sorted_df = filtered_df.sort_values(by='totalstd')
            # Normalize using the full dataset
            norm_totalstd = (sorted_df['totalstd'] - min_std) / (max_std - min_std)
            fig_bar.add_trace(go.Bar(
                x=sorted_df['schools_province'],
                y=sorted_df['totalstd'],
                marker=dict(
                    color=norm_totalstd,
                    colorscale=color_scale,
                ),
            ))
    else:
        # Use data from the current page of the table if no provinces are selected
        page_df = df.iloc[page_current * page_size : (page_current + 1) * page_size]
        if not page_df.empty:
            sorted_page_df = page_df.sort_values(by='totalstd')
            # Normalize using the full dataset
            norm_totalstd = (sorted_page_df['totalstd'] - min_std) / (max_std - min_std)
            fig_bar.add_trace(go.Bar(
                x=sorted_page_df['schools_province'],
                y=sorted_page_df['totalstd'],
                marker=dict(
                    color=norm_totalstd,
                    colorscale=color_scale,
                ),
            ))

    fig_bar.update_layout(
        title='Total Graduated Students per Province',
        xaxis_title='Province',
        yaxis_title='Total Students',
        yaxis=dict(
            autorange=True,
            type='linear'
        ),
        margin={"r":0,"t":50,"l":0,"b":0},
    )

    # Update table data based on selected provinces
    table_data = filtered_df.to_dict('records')

    return fig_map, table_data, fig_bar, selected_provinces, selected_provinces

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)
