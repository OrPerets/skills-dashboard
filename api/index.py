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

# --- Color Handling ---
def determine_color(value):
    """Determine color based on value."""
    color_map = {
        "hot": [15, 20],
        "warm": [6, 14],
        "cold": [0, 5]
    }
    if color_map["cold"][0] <= value <= color_map["cold"][1]:
        return "blue"
    elif color_map["warm"][0] <= value <= color_map["warm"][1]:
        return "yellow"
    elif color_map["hot"][0] <= value <= color_map["hot"][1]:
        return "red"
    return "grey"

def update_z_values_with_colors(z_values):
    """Convert z-values to colors."""
    return [[determine_color(value) for value in row] for row in z_values]

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
dashApp = Dash(__name__, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP])
dashApp.layout = dbc.Container(fluid=True, style={'direction': 'rtl', 'backgroundColor': "#F8F9FA", 'height': "800px"}, children=[
    # --- Navbar ---
    dbc.Navbar(
    dbc.Container([
        dbc.Row(
            [
                dbc.Col(
                    dbc.ButtonGroup(
                        [
                            dbc.InputGroup(
                                [
                                    dbc.Button(
                                        "-",
                                        id="decrease-size-button",
                                        n_clicks=0,
                                        color="primary",
                                        className="me-1",
                                        size="md",
                                        style={"border-radius": "50%"},
                                    ),
                                    dbc.Button(
                                        "↺",
                                        id="reset-view-button",
                                        n_clicks=0,
                                        color="secondary",
                                        className="me-1",
                                        size="md",
                                        style={"border-radius": "50%"},
                                    ),
                                    dbc.Button(
                                        "+",
                                        id="increase-size-button",
                                        n_clicks=0,
                                        color="primary",
                                        size="md",
                                        style={
                                            "border-radius": "50%",
                                            "margin-right": "4px",
                                        },
                                    ),
                                ]
                            ),
                        ]
                    ),
                    width="auto",
                    # This is the key! Use ms-0 instead of ms-auto
                    className="ms-0",  
                ),
                dbc.Col(
                    html.Div(
                        "",
                        className="navbar-brand mb-0 h1",
                        style={
                            "font-family": "Arial, sans-serif",
                            "textAlign": "right",
                        },
                    )
                ),
            ],
            align="center",
            className="g-0",
        ),
    ]),
    style={
        "height": "60px",
        "background": "linear-gradient(to right, #777, #111)",
        "direction": "ltr"
    },
),
    dbc.Row([
        # --- Sidebar ---
        dbc.Col([
            html.H3("מפת חום", style={"textAlign": "center"}),
            # html.H5("תחומי חיים", style={"textAlign": "center"}),
            html.Hr(),
            # --- Filter Section ---
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dcc.Checklist(
                                id='column-checklist',
                                options=[],
                                value=[],
                            ),
                        ],
                        title="בחרו תחומי חיים",
                    ),
                    dbc.AccordionItem(
                        [
                            dcc.RangeSlider(
                                id='value-range-slider',
                                min=0,
                                max=100,
                                step=1,
                                value=[0, 100],
                                marks={i: f'{i}' for i in range(0, 101, 10)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                        ],
                        title="פילטר ערכים",
                    ),
                ],
                start_collapsed=True,
            ),
            html.Br(),
            dbc.Button("בחר הכל / בטל הכל", id='select-all-button', n_clicks=0, color='primary', style={'width': '100%'}),
        ], width=2, style={
    'backgroundColor': '#f8f9fa', 
    'padding': '20px', 
    'fontSize': '18px',
    'marginTop': "5%",
    'boxShadow': '2px 5px 5px 5px rgba(0, 0, 0, 0.5)'  # Add shadow
}),  # Light gray background

        # --- Main Content Area ---
        dbc.Col([
            dcc.Loading(
                id="loading-heatmap",
                type="default",
                children=dcc.Graph(
                    id='heatmap', 
                    config={'displayModeBar': False, 'modeBarButtonsToRemove': ['select2d', 'lasso2d']},
                    style={'width': '100%', 'height': '80vh'}
                ),
            ),
        ], width=10),
    ]),

    # Hidden components for interactivity
    dcc.Store(id='screen-size-store'),
    dcc.Store(id='selected-cell-data'),
    dcc.Store(id='heatmap-size', data={'width': 1100, 'height': 750}),

    # Modal
    dbc.Modal(
        id='modal',
        size='xl',
        is_open=False,
        children=[
            dbc.ModalHeader(dbc.ModalTitle("")),
            dbc.ModalBody(children=[]),
            dbc.ModalFooter(
                dbc.Button("סגור", id='close-modal', className="ml-auto")
            ),
        ],
        style={'direction': 'rtl'}
    ),
])

# --- Callbacks ---
@dashApp.callback(
    Output('heatmap', 'figure'),
    [
        Input('column-checklist', 'value'),
        Input('heatmap-size', 'data'),
        Input('value-range-slider', 'value'),
        Input('reset-view-button', 'n_clicks') 
    ],
    prevent_initial_call=True
)
def update_heatmap(selected_columns, heatmap_size_data, value_range, reset_clicks):
    try:
        ctx = dash.callback_context
        if ctx.triggered and 'reset-view-button' in ctx.triggered[0]['prop_id']:
            # Reset heatmap size when reset button is clicked
            heatmap_size_data = {'width': 1100, 'height': 750}

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

        # Heatmap size
        width = heatmap_size_data.get('width', 1100)
        height = heatmap_size_data.get('height', 750)

        # Create figure
        fig = go.Figure(
            data=go.Heatmap(
                z=z_values_filtered,
                x=list(df_filtered.keys()),
                y=y_axis_labels,
                colorscale='YlOrRd',  # You can experiment with other colorscales
                hoverongaps=False,
                showscale=False,
                colorbar=dict(title="ערך", titleside="right"),  # Hebrew title
                # Add hovertemplate for detailed tooltips
                hovertemplate='<b>%{x}</b><br>' +
                              '<b>%{y}</b><br>' +
                              'ערך: %{z}<extra></extra>' 
            )
        )

        # Update layout
        fig.update_layout(
            xaxis=dict(
                tickangle=0,
                tickfont=dict(size=16, family="Arial, sans-serif"),
                title_text="",
                side="bottom",
                automargin=True,
                constrain="domain"
            ),
            yaxis=dict(
                tickfont=dict(size=16, family="Arial, sans-serif"),
                automargin=True,
                side="left",
            ),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="#f8f9fa",  # Light gray background
            height=height,
            width=width,
            margin=dict(l=10, r=10, t=10, b=10),
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
            figure_data = figure_map.get(x, {}).get(clean_html_string(y))
            if figure_data is None:
                return None, {'display': 'none'}, None, {'display': 'none'}
            figure = figure_data['figure']
            metadata = figure_data['metadata']

            modal_content = [
                dbc.ModalHeader(dbc.ModalTitle(f"{x}, {clean_html_string(y)}")),
                dbc.ModalBody([
                    html.H5(metadata["survey_item"]),
                    dcc.Graph(figure=figure),
                    html.P(metadata["notes"]),
                    html.A("למידע נוסף לחץ כאן", href=metadata["link"], target="_blank"),
                ]),
                dbc.ModalFooter(
                    dbc.Button("סגור", id='close-modal', className="ml-auto")
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