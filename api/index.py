import dash
from dash import dcc, html, Dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from flask import Flask
import json
import os
import re
import logging

# Import your figures_map if needed
from .figures_map import figure_map  # Assuming this file contains your figure data

logging.basicConfig(level=logging.DEBUG)
print("Starting Flask server...")

# Load data from JSON
def load_data(file_path):
    try:
        full_path = os.path.join('public', file_path)
        with open(full_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        df = {key: [row[key] for row in data] for key in data[0]}
        y_axis_categories = df.pop('נושא', None)
        return df, y_axis_categories
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return {}, []

# --- Text Handling ---
def update_y_axis_categories_with_extra_column(y_labels):
    """Update y-axis labels."""
    updated_labels = []
    for label in y_labels:
        if " " in label:
            parent_category, subcategory = label.rsplit(" ", 1)
            updated_label = f"<b>{parent_category}</b> | {subcategory}"
        else:
            updated_label = label
        updated_labels.append(updated_label)
    return updated_labels

def clean_html_string(html_string):
    """Clean an HTML string."""
    clean_text = re.sub(r'<.*?>', '', html_string).strip()
    clean_text = re.sub(r'\s*\|\s*', ' ', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text)
    return clean_text

def convert_AI_label(y_axis_labels):
    """Replace "AI" with "בינה מלאכותית"."""
    for i in range(len(y_axis_labels)):
        if "AI" in y_axis_labels[i]:
            y_axis_labels[i] = y_axis_labels[i].replace("AI", "<b>בינה מלאכותית</b>")

# --- App Setup ---
app = Flask(__name__, static_folder='public')
dashApp = Dash(__name__, server=app, external_stylesheets=[dbc.themes.SANDSTONE])

navbar = html.Div(
    [
        html.Nav(  # Use an HTML nav element for semantic correctness
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.A(
                                    html.H1("מפת חום - תחומי חיים", className="navbar-brand", style={"fontSize": "2rem"}),
                                    href="/",
                                ),
                                width=4,  # Adjust width as needed
                            ),
                        ],
                        justify="between", # Distribute space between columns
                        align="center",
                        style={"height": "100%"}, # Make sure row takes full navbar height
                    )
                ],
                # fluid=True,
            ),
            className="custom-navbar",  # Class for custom styling
        ),
    ]
)

dashApp.layout = dbc.Container(fluid=True, style={'direction': 'rtl', 'backgroundColor': "#F8F9FA"}, children=[
    # --- Navbar ---
    dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.A(
                            html.H2("מפת חום - תחומי חיים", className="navbar-brand", style={"fontSize": "30px", 'color': 'white'}),  # Larger, white text
                            # href="/",  # Or your desired link
                        ),
                        # Class name for styling
                        # className="ms-0", # Keep left alignment
                    ),
                ],
                # align="center",
                # className="g-0",  # Remove horizontal gaps
            ),

            # Add a subtle separator line within the navbar (optional)
            html.Hr(style={"borderColor": "rgba(255, 255, 255, 0.3)", "margin": "10px 0"})
        ],
        fluid=True, # Fill container width
    ),
    color="primary",  # Use your primary color or a specific hex code #e.g., color="#007bff"
    dark=True,       # Darkens the background
    style={"height": "auto", "padding": "15px 0", "direction": "rtl"},
),

    # --- Main Content ---
    dbc.Row([
        # --- Sidebar ---
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("בחרו תחומי חיים", className="card-title")),
                dbc.CardBody([
                    dcc.Checklist(
                        id='column-checklist',
                        options=[],
                        value=[],
                        labelStyle={'display': 'block', 'margin-left': '10px'}
                    ),
                    dbc.Button("בחר הכל / בטל הכל", id='select-all-button', n_clicks=0, color='primary', style={'width': '100%', 'margin-top': '10px'}),
                ]),
            ], style={'margin-bottom': '20px'}),
            dbc.Card([
                dbc.CardHeader(html.H5("פילטר ערכים", className="card-title")),
                dbc.CardBody([
                    dcc.RangeSlider(
                        id='value-range-slider',
                        min=0,
                        max=100,
                        step=1,
                        value=[0, 100],
                        marks={i: f'{i}' for i in range(0, 101, 10)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                ]),
            ], style={'margin-bottom': '20px', 'display': "none"}),
            dbc.Card([
                dbc.CardHeader(html.H5("בחרו צבעים", className="card-title")),
                dbc.CardBody([
                    dcc.Dropdown(
                        id='colorscale-dropdown',
                        options=[
                            {'label': 'חם', 'value': 'Reds'},
                            {'label': 'קר', 'value': 'Cividis'},
                            {'label': 'פלזמה', 'value': 'Plasma'},
                            {'label': 'כחול', 'value': 'Blues'},
                            {'label': 'ירוק', 'value': 'Greens'},
                        ],
                        value='Reds',
                        clearable=False
                    ),
                ]),
            ]),
        ], xs=12, sm=12, md=3, lg=2, style={
            'backgroundColor': '#f8f9fa', 
            'padding': '20px', 
            'fontSize': '18px',
            'marginTop': "20px"
        }),  # Sidebar styling

        # --- Main Content Area ---
        dbc.Col([
            dbc.Card([
                # dbc.CardHeader(html.H5("מפת חום", className="card-title")),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-heatmap",
                        type="default",
                        children=dcc.Graph(
                            id='heatmap', 
                            config={
                                'displayModeBar': False, 
                                'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
                                'scrollZoom': True
                            },
                            style={'width': '100%', 'height': '100%'}
                        ),
                    ),
                ]),
            ], style={'margin-top': '20px', 'height': "800px"}),
        ], xs=12, sm=12, md=9, lg=10),
    ]),

    # Hidden components for interactivity
    dcc.Store(id='screen-size-store'),
    dcc.Store(id='selected-cell-data'),
    # dcc.Store(id='heatmap-size', data={'width': 1400, 'height': 750}),
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0, max_intervals=1),

    dbc.Modal(
    id='modal',
    size='xl',  # Increased size to extra-large to take up more screen space
    is_open=False,
    children=[
        dbc.ModalHeader(
            dbc.ModalTitle(""),
            close_button=False,  # Keep close button visible for easy closing
            style={
                "backgroundColor": "#F8F9FA",
                "border-bottom": "1px solid #dee2e6"
            }
        ),
        dbc.ModalBody(children=[],
            style={
                'backgroundColor': '#f8f9fa',  # Light grey consistent with overall dashboard styling
                'padding': '20px'
            }
        ),
        dbc.ModalFooter(
            dbc.Button("סגור", id='close-modal', className="ml-auto", style={"font-size": "1.2rem", "padding": "10px 20px"})
        ),
    ],
    style={
        'direction': 'rtl',
        # 'maxWidth': '95%',  # Ensure the modal doesn't take up the entire screen but is wider
        'margin': '0 auto',  # Center the modal in the screen
        'width': "90%"
    }
)
])

dashApp.clientside_callback(
    """
    function(n_intervals) {
        return {
            width: window.innerWidth,
            height: window.innerHeight
        };
    }
    """,
    Output('screen-size-store', 'data'),
    [Input('interval-component', 'n_intervals')]
)

def change_x_labels(x_labels):
    x_axis_labels_modified = []
    for label in x_labels:
        if " " in label:  # Check for multiple words
            modified_label = label.replace(" ", "<br>") # Insert <br> tag
            x_axis_labels_modified.append(modified_label)
        else:
            x_axis_labels_modified.append(label)
    return ['<b>' + label + '</b>' for label in x_axis_labels_modified]

@dashApp.callback(
    Output('heatmap', 'figure'),
    [
        Input('column-checklist', 'value'),
        Input('value-range-slider', 'value'),
        Input('colorscale-dropdown', 'value'),
        Input('screen-size-store', 'data'),
    ],
    prevent_initial_call=False
)
def update_heatmap(selected_columns, value_range, selected_colorscale, screen_size_data):
    try:
        # Load data
        df, y_axis_categories = load_data('example.json')

        # Filter data
        df_filtered = {key: df[key] for key in selected_columns} if selected_columns else df
        z_values = list(zip(*df_filtered.values()))
        min_val, max_val = value_range
        z_values_filtered = [
            [value if min_val <= value <= max_val else None for value in row]
            for row in z_values
        ]

        # Format labels
        y_axis_labels = update_y_axis_categories_with_extra_column(y_axis_categories)
        convert_AI_label(y_axis_labels)

        # Adjust heatmap size based on screen dimensions
        if screen_size_data:
            width = screen_size_data.get('width', 1100)
            height = screen_size_data.get('height', 750)
            adjusted_width = width * 0.75  # Adjust as needed
            adjusted_height = height * 0.8
        else:
            adjusted_width = 1100
            adjusted_height = 750

        # Create figure
        fig = go.Figure(
            data=go.Heatmap(
                z=z_values_filtered,
                x=change_x_labels(list(df_filtered.keys())),
                y=y_axis_labels,
                colorscale=selected_colorscale,
                hoverongaps=False,
                showscale=False,
                ygap=2,
                xgap=2,
                colorbar=dict(title="ערך", titleside="right"),
                hovertemplate='לחץ כאן עבור מידע נוסף בנושא <br> %{x} + %{y}<extra></extra>' # Updated hovertemplate
            ),
        )

        # Update layout
        fig.update_layout(
            font=dict(size=14, family="Arial, sans-serif"),
            xaxis=dict(
                tickangle=0,
                tickfont=dict(size=16, family="Arial, sans-serif"),
                title_text="",
                side="bottom",
                automargin=True,
                constrain="domain"
            ),
            yaxis=dict(
                tickfont=dict(size=18, family="Arial, sans-serif"),
                automargin=True,
                side="left",
            ),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="white",
            height=adjusted_height,
            width=adjusted_width,
            margin=dict(l=10, r=10, t=10, b=10),
            hoverlabel=dict(
        bgcolor="white",       # Background color of the hover label
        bordercolor="black",   # Border color of the hover label
        font_size=16,       # Font size of the hover label
        font_family="Arial",  # Font family of the hover label
    )
        )

        return fig

    except Exception as e:
        logging.error(f"Error updating heatmap: {e}")
        fig = go.Figure()
        fig.add_annotation(text="שגיאה בטעינת הנתונים. אנא נסה שוב מאוחר יותר.",
                           xref="paper", yref="paper",
                           showarrow=False,
                           font=dict(size=20))
        return fig

@dashApp.callback(
    [Output('column-checklist', 'options'),
     Output('column-checklist', 'value')],
    Input('select-all-button', 'n_clicks'),
    State('column-checklist', 'options'),
)
def update_checklist_options(n_clicks, current_options):
    try:
        df, _ = load_data('example.json')
        options = [{'label': "    " + key, 'value': key} for key in df.keys()]
        if n_clicks == 0:  # Initial state
            return options, []
        elif n_clicks % 2 == 1:  # Select all
            return options, [option['value'] for option in options]
        else:  # Deselect all
            return options, []
    except Exception as e:
        logging.error(f"Error updating checklist options: {e}")
        return [], []

@dashApp.callback(
    Output('modal', 'is_open'),
    [Input('heatmap', 'clickData'),
     Input('close-modal', 'n_clicks')],
    [State('modal', 'is_open')],
)
def toggle_modal(clickData, n_clicks_close, is_open):
    ctx = dash.callback_context
    if ctx.triggered:
        prop_id = ctx.triggered[0]['prop_id']
        if 'heatmap' in prop_id and clickData:
            return True
        elif 'close-modal' in prop_id and n_clicks_close:
            return False
    return is_open

@dashApp.callback(
    [Output('modal', 'children'),
     Output('modal', 'style')],
    Input('heatmap', 'clickData'),
    prevent_initial_call=True
)
def update_modal_content(clickData):
    try:
        if clickData:
            clicked_point = clickData['points'][0]
            x = clicked_point['x']
            y = clicked_point['y']
            value = clicked_point['z']

            figure_data = None  # Replace with actual data retrieval
            figure_data = figure_map.get(clean_html_string(x), {}).get(clean_html_string(y))
            if figure_data is None:
                return dash.no_update, {'display': 'none'}
            figure = figure_data['figure']
            metadata = figure_data['metadata']

            modal_content = [
                dbc.ModalHeader(
        html.Div(  # Wrap title in a div for better control
            dbc.ModalTitle(f"{clean_html_string(x)}, {clean_html_string(y)}", style={"fontWeight": "bold", "fontSize": "32px"}),
            style={"textAlign": "center", "width": "100%"} # Center the div
        ),
        # close_button=False, 
        style={"padding": "15px"}
    ),
                dbc.ModalBody([
                    html.H5(metadata["survey_item"], style={
                "textAlign": "center", # Center the H5
                "marginBottom": "20px", # Add margin below
                # ... other H5 styles ... e.g., color, font-size
            }),
                    dcc.Graph(figure=figure, config={'displayModeBar': False}),
                    html.P(metadata["notes"]),
                    html.A("למידע נוסף לחץ כאן", href=metadata["link"], target="_blank", style={"display": "block", "textAlign": "center", "color": "black", "marginTop": "10px", "fontSize": "18px"}),
                ], style={
        'backgroundColor': '#f8f9fa', 
        'padding': '20px'
    }),
                dbc.ModalFooter(
                    dbc.Button("סגור", id='close-modal', className="ml-auto", style={"backgroundColor": "lightgray", "color": "black", "display": "none"})
                ),
            ]
            modal_style = {'direction': 'rtl'}
            return modal_content, modal_style
        else:
            return [], {}
    except Exception as e:
        logging.error(f"Error updating modal content: {e}")
        return [], {}

@dashApp.callback(
    Output('heatmap-size', 'data'),
    [Input('increase-size-button', 'n_clicks'),
     Input('decrease-size-button', 'n_clicks')],
    State('heatmap-size', 'data')
)
def update_heatmap_size(increase_clicks, decrease_clicks, current_size):
    try:
        # Start with current width and height
        new_width = current_size['width']
        new_height = current_size['height']
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_size
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'increase-size-button':
            new_width *= 1.1
            new_height *= 1.1
        elif button_id == 'decrease-size-button':
            new_width *= 0.9
            new_height *= 0.9
        return {'width': int(new_width), 'height': int(new_height)}
    except Exception as e:
        logging.error(f"Error updating heatmap size: {e}")
        return current_size

if __name__ == '__main__':
    app.run(debug=True, port=8051)
