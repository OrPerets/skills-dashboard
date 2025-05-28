import dash
from dash import dcc, html, Dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.colors
from flask import Flask
import json
import os
import re
import logging

# Import your figures_map if needed
from .figures_map import figure_map  # Assuming this file contains your figure data

# Define a safe color palette as fallback
SAFE_COLORS = [
    '#88CCEE', '#44AA99', '#117733', '#332288', '#DDCC77',
    '#999933', '#CC6677', '#882255', '#AA4499', '#DDDDDD'
]

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
    if html_string is None:
        return ""
    # קודם כל להחליף תגיות <br> ברווח, כדי שלא ייעלמו
    text = re.sub(r'<br\s*/?>', ' ', html_string)
    # אחר-כך להסיר את כל שאר התגיות
    text = re.sub(r'<.*?>', '', text)
    # להמיר מפריד אנכי לרווח
    text = re.sub(r'\s*\|\s*', ' ', text)
    # לצמצם רווחים מיותרים
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def convert_AI_label(y_axis_labels):
    """Replace "AI" with "בינה מלאכותית"."""
    for i in range(len(y_axis_labels)):
        if "AI" in y_axis_labels[i]:
            y_axis_labels[i] = y_axis_labels[i].replace("AI", "<b>בינה מלאכותית</b>")

# --- App Setup ---
app = Flask(__name__, static_folder='public')
dashApp = Dash(__name__, server=app, external_stylesheets=[
    dbc.themes.SANDSTONE,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
])

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
                            {"label": "רמזור", "value": "R"},
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
        size='lg',
        centered=True,
        is_open=False,
        fade=True,
        children=[
            dbc.ModalHeader(
                dbc.ModalTitle(""),
                close_button=True,
                className="custom-modal-header border-0 pb-0"
            ),
            dbc.ModalBody(
                children=[],
                style={
                    'backgroundColor': '#f8f9fa',
                    'padding': '0 2rem 2rem 2rem'
                }
            ),
            dbc.ModalFooter(
                className="border-0 pt-0",
                children=[]
            ),
        ],
        style={
            'direction': 'rtl'
        }
    )
])

def original_row_key(y_label):
    txt = clean_html_string(y_label)
    if "|" in y_label:
        txt = txt.split("|")[0]
    return txt.strip()

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

# Clientside callback for download functionality
dashApp.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks && n_clicks > 0) {
            const graphDiv = document.querySelector('.modal .js-plotly-plot');
            if (graphDiv && window.Plotly) {
                window.Plotly.downloadImage(graphDiv, {
                    format: 'png',
                    width: 800,
                    height: 600,
                    filename: 'skills_dashboard_chart'
                });
            }
        }
        return '';
    }
    """,
    Output('download-btn', 'title'),
    [Input('download-btn', 'n_clicks')],
    prevent_initial_call=True
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
            adjusted_width = width * 0.8  # Adjust as needed
            adjusted_height = height * 0.85
        else:
            adjusted_width = 1100
            adjusted_height = 750

        # Define traffic-light color scheme matching the provided image
        traffic_light_colors = [
            [0.0, "rgba(34,139,34,0.9)"],     # Forest Green (lowest values)
            [0.1, "rgba(50,205,50,0.9)"],     # Lime Green
            [0.2, "rgba(124,252,0,0.9)"],     # Lawn Green
            [0.3, "rgba(173,255,47,0.9)"],    # Green Yellow
            [0.4, "rgba(255,255,0,0.9)"],     # Yellow
            [0.5, "rgba(255,215,0,0.9)"],     # Gold
            [0.6, "rgba(255,165,0,0.9)"],     # Orange
            [0.7, "rgba(255,140,0,0.8)"],     # Dark Orange
            [0.8, "rgba(255,69,0,0.8)"],      # Orange Red
            [0.9, "rgba(255,0,0,0.8)"],       # Red
            [1.0, "rgba(178,34,34,0.8)"],     # Fire Brick (highest values)
        ]

        if selected_colorscale == "R":
            selected_colorscale = traffic_light_colors
        else:
            # Use the traffic-light scheme as default when not using built-in schemes
            selected_colorscale = traffic_light_colors

        # Create figure
        fig = go.Figure(
            data=go.Heatmap(
                z=z_values_filtered,
                x=change_x_labels(list(df_filtered.keys())),
                y=y_axis_labels,
                colorscale=selected_colorscale,
                hoverongaps=False,
                showscale=False,
                ygap=3,
                xgap=3,
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
            point = clickData['points'][0]
            col_key = clean_html_string(point['x'])
            row_key = original_row_key(point['y'])
            
            print("COL KEY", col_key)
            print("ROW KEY", row_key)
            print("Available figure_map keys:", list(figure_map.keys())[:5] if figure_map else "No keys")
            if col_key in figure_map:
                print(f"Available row keys for {col_key}:", list(figure_map[col_key].keys())[:5])
            
            # Try both mappings since the structure might be reversed
            figure_data = figure_map.get(col_key, {}).get(row_key)
            if figure_data is None:
                figure_data = figure_map.get(row_key, {}).get(col_key)
            if figure_data is None:
                return dash.no_update, {'display': 'none'}

            figure = figure_data['figure']
            metadata = figure_data['metadata']

            # Enhance the figure with better styling
            enhanced_figure = figure
            enhanced_figure.update_layout(
                template="simple_white",
                margin=dict(l=0, r=0, t=10, b=0),
                height=350,
                font=dict(size=16),
                hovermode="x unified",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="white"
            )
            
            # Apply Safe color palette based on chart type
            if enhanced_figure.data:
                trace = enhanced_figure.data[0]
                
                # Try to get Safe colors from plotly, fall back to our defined colors
                try:
                    safe_colors = plotly.colors.qualitative.Safe
                except AttributeError:
                    safe_colors = SAFE_COLORS
                
                if hasattr(trace, 'marker') and hasattr(trace.marker, 'color'):
                    # For bar charts and scatter plots
                    trace.marker.color = safe_colors[0]
                elif hasattr(trace, 'marker') and hasattr(trace.marker, 'colors'):
                    # For pie charts
                    trace.marker.colors = safe_colors[:len(trace.labels) if hasattr(trace, 'labels') else 4]

            # Generate insight text based on data
            insight_text = f"💡 נתונים מעניינים עבור {col_key} ב{row_key}"
            if metadata.get("notes"):
                insight_text = f"💡 {metadata['notes'][:100]}..."

            # Create metadata badges
            metadata_badges = []
            if metadata.get("source"):
                metadata_badges.append(
                    dbc.Badge(f"מקור: {metadata['source']}", color="primary", className="metadata-badge badge-primary-custom")
                )
            if metadata.get("measurement_method"):
                metadata_badges.append(
                    dbc.Badge(f"שיטת מדידה", color="info", className="metadata-badge badge-info-custom")
                )
            
            # Add sample size badge (mock data)
            metadata_badges.append(
                dbc.Badge("n=1,200", color="secondary", className="metadata-badge badge-secondary-custom")
            )

            modal_content = [
                dbc.ModalHeader(
                    dbc.Container([
                        html.Div([
                            html.I(className="fas fa-info-circle help-icon", id="help-icon"),
                            html.H4(f"{col_key}", className="modal-title-main mb-0 fw-bold"),
                        ], style={"display": "flex", "alignItems": "center"}),
                        html.Small(f"{row_key}", className="modal-title-sub text-muted")
                    ], fluid=True),
                    close_button=True,
                    className="custom-modal-header border-0 pb-0"
                ),
                dbc.ModalBody([
                    dbc.Container([
                        # Survey item with enhanced styling
                        html.Div(
                            metadata.get("survey_item", "פריט סקר לא זמין"),
                            className="survey-item-text"
                        ),
                        
                        # Metadata badges
                        dbc.Row(
                            metadata_badges,
                            className="mt-3 mb-3"
                        ),
                        
                        # Enhanced graph container
                        html.Div([
                            dcc.Graph(
                                figure=enhanced_figure, 
                                config={'displayModeBar': False}
                            )
                        ], className="graph-container"),
                        
                        # Insight text
                        html.Div(
                            insight_text,
                            className="insight-text"
                        ),
                        
                    ], fluid=True)
                ], style={
                    'backgroundColor': '#f8f9fa',
                    'padding': '0 2rem 2rem 2rem'
                }),
                dbc.ModalFooter([
                    dbc.Row([
                        dbc.Col([
                            # Left side - additional link
                            html.A(
                                "למידע נוסף לחץ כאן", 
                                href=metadata.get("link", "#"), 
                                target="_blank",
                                style={
                                    "color": "#0d6efd", 
                                    "textDecoration": "none",
                                    "fontSize": "1.1rem",
                                    "fontWeight": "600"
                                }
                            ) if metadata.get("link") else html.Div()
                        ], width="auto"),
                        dbc.Col([
                            # Right side - action buttons
                            dbc.ButtonGroup([
                                dbc.Button(
                                    [html.I(className="fas fa-download me-2"), "הורד PNG"],
                                    color="outline-primary",
                                    className="btn-outline-custom",
                                    id="download-btn"
                                ),
                                dbc.Button(
                                    "סגור",
                                    id='close-modal',
                                    color="outline-secondary",
                                    className="btn-outline-custom"
                                )
                            ], className="action-buttons")
                        ], width="auto", className="ms-auto")
                    ], justify="between", align="center", className="w-100")
                ], className="border-0 pt-0")
            ]
            
            # Add popover for help icon
            modal_content.append(
                dbc.Popover(
                    dbc.PopoverBody("המדדים מחושבים על בסיס נתוני סקרים לאומיים ומחקרים אקדמיים"),
                    target="help-icon",
                    trigger="hover",
                    placement="bottom"
                )
            )
            
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
