import pandas as pd
import json
from urllib.request import urlopen
import pandas as pd
import plotly.graph_objects as go

with urlopen("https://raw.githubusercontent.com/chingchai/OpenGISData-Thailand/master/provinces.geojson") as response:
    provinces = json.load(response)

with urlopen("https://gpa.obec.go.th/reportdata/pp3-4_2566_province.json") as response:
    data = json.load(response)
    df = pd.DataFrame(data)

fig = go.Figure(go.Choroplethmapbox(geojson=provinces, 
                                    locations=df.schools_province, 
                                    z=df.totalstd, 
                                    featureidkey="properties.pro_th",
                                    colorscale="Viridis",
                                    marker_opacity=0.2, 
                                    marker_line_width=0))

fig.update_layout(mapbox_style="carto-positron",
                  mapbox_zoom=5.2, mapbox_center = {"lat": 13.1111, "lon": 99.9390})
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()