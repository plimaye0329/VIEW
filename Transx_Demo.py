from dash import Dash, html, dash_table, dcc, Input, Output, no_update, callback
import pandas as pd
import plotly.express as px
import os
import base64

# Load the space-separated data with no header
df = pd.read_csv('band1_3.txt', delim_whitespace=True, header=None)

# Rename columns
df.columns = ['col1', 'col2', 'MJD', 'Burst_DM', 'col5', 'col6', 'col7', 'col8', 'ImagePath', 'col10', 'col11']

# Create image filenames by modifying ImagePath
df['ImageFilename'] = df['ImagePath'].apply(lambda x: os.path.basename(x).replace('.png', '_replot.png'))

# Image directory
image_directory = './'

# Function to encode image
def encode_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Image not found: {image_path}")
        return None

# Create the scatter plot
fig = px.scatter(df, x='MJD', y='Burst_DM', title='Burst DM vs MJD')

# Disable native hovertemplate and pass filenames in customdata
fig.update_traces(
    hoverinfo="none",
    hovertemplate=None,
    customdata=df[['ImageFilename', 'MJD', 'Burst_DM']].values  # Include MJD and Burst_DM in customdata
)

# Initialize Dash app
app = Dash()

app.layout = html.Div([
    html.H1('TransientX Viewer'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10),
    dcc.Graph(id="scatter-plot", figure=fig, clear_on_unhover=True),
    dcc.Tooltip(id="graph-tooltip"),
])

# Callback for image tooltip on hover
@callback(
    Output("graph-tooltip", "show"),
    Output("graph-tooltip", "bbox"),
    Output("graph-tooltip", "children"),
    Input("scatter-plot", "hoverData"),
)
def display_hover(hoverData):
    if hoverData is None:
        return False, no_update, no_update

    pt = hoverData["points"][0]
    bbox = pt["bbox"]
    custom_data = pt.get("customdata", [])
    
    if not custom_data or len(custom_data) < 3:
        return False, no_update, no_update

    image_filename, mjd, burst_dm = custom_data

    image_path = os.path.join(image_directory, image_filename)
    encoded = encode_image(image_path)

    if not encoded:
        return False, no_update, no_update

    # Update tooltip content
    children = [
        html.Div([
            html.Img(src=f"data:image/png;base64,{encoded}", style={"width": "400px", "height": "auto", "border": "2px solid #ccc"}),
            html.P(f"MJD: {mjd}", style={"fontSize": "12px", "marginTop": "10px"}),
            html.P(f"Burst DM: {burst_dm}", style={"fontSize": "12px"}),
            html.P(f"{image_filename}", style={"fontSize": "10px", "wordBreak": "break-all"})
        ], style={'width': '420px', 'white-space': 'normal'})
    ]

    return True, bbox, children

if __name__ == '__main__':
    app.run(debug=True)


