import dash
from dash import dcc, html, Dash
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_dangerously_set_inner_html
import plotly.graph_objects as go
from flask import Flask, send_from_directory
import json
import os
from .figures_map import *
import re
# import subprocess

import logging
logging.basicConfig(level=logging.DEBUG)

print("Starting Flask server for Vercel...")


def load_data(file_path):
    # Construct the full path to the JSON file in the public folder
    full_path = os.path.join('public', file_path)

    # Read the JSON file
    with open(full_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Convert the JSON structure to the format used in the app
    df = {key: [row[key] for row in data] for key in data[0]}
    y_axis_categories = df.pop('נושא', None)  # Extract and remove the 'נושא' column
    df_text = df.copy()  # For text display without dropping columns
    return df, y_axis_categories, df_text

app = Flask(__name__, static_folder='public')
dashApp = Dash(__name__, server=app)
dashApp.layout = html.Div(style={
    'display': 'flex',
    'flexDirection': 'row',
    'height': '120vh',  # Full viewport height
    'backgroundColor': '#ecf0f1',  # Grey background
    'direction': 'rtl',
    'margin': 0,
    'padding': 0,
    'boxSizing': 'border-box',
}, children=[
    # Sidebar
    html.Div(style={
        'position': 'fixed',  # Fixed position to float
        'top': '50%',
        'left': 0,
        'transform': 'translateY(-50%)',
        'width': '250px',  # Fixed width for sidebar
        'backgroundColor': '#34495e',
        'padding': '20px',
        'color': '#ecf0f1',
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'flex-start',
        'boxShadow': '2px 0 10px rgba(0, 0, 0, 0.2)',
        'borderRadius': '0 10px 10px 0',
        'zIndex': 1000,  # Make sure it is above other elements
        'transition': 'transform 0.3s ease-in-out',
        'boxSizing': 'border-box'
    }, children=[
        html.H2("תפריט", style={
            'color': '#ecf0f1',
            'fontSize': '24px',
            'marginBottom': '20px',
            'direction': 'rtl'
        }),
        html.Label("בחרו תחומי חיים", style={
            'fontSize': '18px',
            'marginBottom': '10px',
            'direction': 'rtl'
        }),
        dcc.Checklist(
            id='column-checklist',
            options=[],
            value=[],
            style={
                'fontSize': '16px',
                'color': '#ecf0f1',
                'marginBottom': '20px',
                'direction': 'rtl',
                'lineHeight': '2.5'
            }
        ),
        html.Button("בחר הכל / בטל הכל", id='select-all-button', n_clicks=0, style={
            'fontSize': '16px',
            'backgroundColor': '#1abc9c',
            'color': '#ffffff',
            'border': 'none',
            'padding': '10px 20px',
            'borderRadius': '5px',
            'cursor': 'pointer',
            'marginTop': '10px',
            'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.3)',
            'direction': 'rtl'
        })
    ]),
    # Main Content
    html.Div(style={
        'flex': 1,  # Take remaining space
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'justifyContent': 'center',
        'backgroundColor': '#ecf0f1',
        'padding': '20px',
        'boxSizing': 'border-box',
        'marginLeft': '250px'  # To prevent overlap with floating sidebar
    }, children=[
        html.Div(style={
            'position': 'fixed',
            'top': '10px',
            'right': '10px',
            'zIndex': 1001,  # Above the main content
            'display': 'flex',
            'flexDirection': 'row',
            'gap': '10px'
        }, children=[
            html.Button("הגדל", id='increase-size-button', n_clicks=0, style={
                'fontSize': '16px',
                'backgroundColor': '#2980b9',
                'color': '#ffffff',
                'border': 'none',
                'padding': '10px 20px',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.3)',
                'direction': 'rtl'
            }),
            html.Button("הקטן", id='decrease-size-button', n_clicks=0, style={
                'fontSize': '16px',
                'backgroundColor': '#c0392b',
                'color': '#ffffff',
                'border': 'none',
                'padding': '10px 20px',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.3)',
                'direction': 'rtl'
            })
        ]),
        html.H1("מפת חום - תחומי החיים", style={
            'textAlign': 'center',
            'color': '#2c3e50',
            'fontSize': '32px',
            'marginBottom': '20px',
            'fontFamily': 'Arial, sans-serif',
            'direction': 'rtl',
            'marginTop': "-10%"
        }),
        dcc.Graph(id='heatmap', config={'clickmode': 'event+select', 'displayModeBar': False}, style={
            # 'width': '100%',
            # 'height': '100%',
            'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.1)',
        }),
    ]),
    dcc.Store(id='screen-size-store'),
    html.Script('''
    (function() {
        function sendScreenSize() {
            const width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
            const height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;

            if (window.dash_clientside && window.dash_clientside.eventData) {
                window.dash_clientside.eventData.width = width;
                window.dash_clientside.eventData.height = height;
            } else {
                window.dash_clientside = {eventData: {width: width, height: height}};
            }
        }

        // Send initial screen size on page load
        sendScreenSize();

        // Send screen size when resizing
        window.addEventListener("resize", sendScreenSize);
    })();
    '''),
    # Modal
    html.Div(id='overlay', style={
    'display': 'none',  # Hidden by default
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'width': '100%',
    'height': '100%',
    'backgroundColor': 'rgba(0, 0, 0, 0.5)',  # Semi-transparent overlay
    'zIndex': 2000
    }),
    html.Div(id='modal', style={'display': 'none', 'direction': 'rtl'}),

    dcc.Store(id='selected-cell-data'),
    dcc.Store(id='heatmap-size', data={'width': 1100, 'height': 750}),  # Store for heatmap size,
])


def get_screen_size():
    return 1100, 700

# Define the color map to distinguish between hot and cold values
color_map = {
    "hot": [15,20],   # Example: Values between 7-10 are "hot"
    "warm": [6, 14],   # Example: Values between 4-6 are "warm"
    "cold": [0, 5]    # Example: Values between 0-3 are "cold"
}

def determine_color(value):
    """Function to determine color based on the value using the predefined color_map."""
    if color_map["cold"][0] <= value <= color_map["cold"][1]:
        return "blue"  # Cold values will be blue
    elif color_map["warm"][0] <= value <= color_map["warm"][1]:
        return "yellow"  # Warm values will be yellow
    elif color_map["hot"][0] <= value <= color_map["hot"][1]:
        return "red"  # Hot values will be red
    return "grey"  # Default color for values that don't fit any category

def update_z_values_with_colors(z_values):
    """Convert z-values to colors based on the color map"""
    z_colors = []
    for row in z_values:
        z_colors.append([determine_color(value) for value in row])
    return z_colors

def update_y_axis_categories(y_axis_categories):
    """
    Function to update y-axis categories such that if the value contains specific terms,
    only those terms will be bolded in the label.
    """
    terms_to_bold = ['AI', 'תחומי חיים כללי', 'פתרון בעיות', 'עסקאות', 'תקשור', 'ניהול מידע']
    updated_categories = []
    for category in y_axis_categories:
        updated_category = category
        for term in terms_to_bold:
            if term in category:
                updated_category = updated_category.replace(term, f'<b>{term}</b>')
        updated_categories.append(updated_category)
    return updated_categories

def update_y_axis_categories_with_extra_column(y_labels):
    """
    Update y-axis labels to include an additional column with correct bolding.
    Extract parent category and subcategory from y_labels directly.
    """
    updated_labels = []
    for label in y_labels:
        # Split the label into parent and subcategory
        if " " in label:
            parent_category, subcategory = label.rsplit(" ", 1)  # Split by the last space
            updated_label = f"<span style='display: flex; justify-content: space-between'><span style='text-align: right;'><b>{parent_category}</b></span> \t | \t <span style='text-align: left;'>{subcategory}</span></span>"
        else:
            # If there's no space, use the label as-is
            updated_label = label
        updated_labels.append(updated_label)

    return updated_labels

def update_y_axis_categories_grouped(y_labels):
    """
    Update y-axis labels to display the bolded category only once per group.
    Subsequent rows in the group will only display the subcategory.
    """
    updated_labels = []
    current_category = None

    for label in y_labels:
        # Split the label into parent category and subcategory
        if " " in label:
            parent_category, subcategory = label.rsplit(" ", 1)  # Split by the last space
            
            # Add the parent category only if it has changed
            if parent_category != current_category:
                updated_labels.append(f"<b>{parent_category}</b>")
                current_category = parent_category
            else:
                updated_labels.append("")  # Leave subsequent rows blank for the same category

            # Always add the subcategory
            updated_labels[-1] += f" | {subcategory}"
        else:
            # If there's no space, use the label as-is
            updated_labels.append(label)

    return updated_labels

def convert_AI_label(y_axis_labels):
    for i in range(len(y_axis_labels)):
        if "AI" in y_axis_labels[i]:
            y_axis_labels[i] = y_axis_labels[i].replace("AI", "<b>בינה מלאכותית</b>")


@dashApp.callback(
    Output('heatmap', 'figure'),
    [Input('column-checklist', 'value'),
     Input('screen-size-store', 'data')]
)
def update_heatmap(selected_columns, screen_size_data):
    if screen_size_data is None:
        screen_size_data = {'width': 1200, 'height': 750}  
    df, y_axis_categories, _ = load_data('example.json')  # Load JSON instead of Excel

    # Filter columns based on selection
    df_filtered = {key: df[key] for key in selected_columns} if selected_columns else df

    # Convert dict to 2D list for heatmap input
    z_values = list(zip(*df_filtered.values()))

    z_colors = update_z_values_with_colors(z_values)

    y_axis_labels = update_y_axis_categories_with_extra_column(y_axis_categories)

    formatted_labels = [
        dash_dangerously_set_inner_html.DangerouslySetInnerHTML(label)
        for label in y_axis_labels
    ]
    convert_AI_label(y_axis_labels)
    width, height = get_screen_size()
    #width = screen_size_data.get('width', 1200)
    #height = screen_size_data.get('height', 750)
    print(width, height)
    fig = go.Figure(
    data=go.Heatmap(
        z=z_values,  # Convert dict values to 2D list
        x=list(df_filtered.keys()),
        y=y_axis_labels,  # Apply bold formatting to important categories
        colorscale=[
            [0.0, '#66C2A5'],  # Green
            [0.2, '#FEE08B'],  # Yellow
            [0.4, '#FDAE61'],  # Orange
            [0.6, '#F46D43'],  # Light Red
            [0.8, '#D73027'],  # Red
            [1.0, '#A50026']   # Dark Red
        ],
        showscale=False
        )
    )
    

    # Update layout to set a consistent font style
    fig.update_layout(
        title_x=0.5,
        title_font=dict(size=24, family="Arial, sans-serif"),
        xaxis=dict(
            tickangle=0,  # Horizontal labels
            tickfont=dict(size=16, family="Arial", color='#2c3e50'),
            title_text="",
            side="bottom",   # Keep labels at the top
            automargin=True,
            constrain="domain"  # Ensure full domain is used for scaling
        ),
        yaxis=dict(
            tickfont=dict(size=16, family="Arial"),
            automargin=True,
            side="left",
            # ticklabelposition="outside right",
        ),
        plot_bgcolor="rgba(0,0,0,0)",           # Transparent background
        paper_bgcolor="rgba(255,255,255,1)",   # White figure background
        height=int(height*0.9),                    # Adjust for the screen size
        width=int(width*0.85),                      # Adjust for the screen size
        margin=dict(l=10, r=50, t=10, b=10), # Minimal margins to reduce empty spaces
    )
    return fig

@dashApp.callback(
    Output('column-checklist', 'options'),
    Output('column-checklist', 'value'),
    Input('select-all-button', 'n_clicks'),
    State('column-checklist', 'options'),
)
def update_checklist_options(n_clicks, current_options):
    df, _, _ = load_data('example.json')  # Load JSON instead of Excel
    options = [{'label': key, 'value': key} for key in df.keys()]  # Keys as column names

    if n_clicks == 0:  # Initial state
        return options, []
    elif n_clicks % 2 == 1:  # Select all
        return options, [option['value'] for option in options]
    else:  # Deselect all
        return options, []

def get_graph_html(fig):
    return fig.to_html(full_html=False)

def clean_html_string(html_string):
    """
    Clean an HTML string, extract the text content, and remove extra spaces and separators.
    """
    # Remove HTML tags
    clean_text = re.sub(r'<.*?>', '', html_string).strip()
    # Replace the "|" separator with a single space
    clean_text = re.sub(r'\s*\|\s*', ' ', clean_text)
    # Remove extra spaces
    clean_text = re.sub(r'\s+', ' ', clean_text)
    return clean_text

@dashApp.callback(
    [Output('selected-cell-data', 'data'),
     Output('modal', 'style'),
     Output('modal', 'children'),
     Output('overlay', 'style')],
    [Input('heatmap', 'clickData'),
     Input({'type': 'close-modal', 'index': ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def manage_selected_cell_and_modal(clickData, close_button_clicks):
    # Check the context to see what triggered the callback
    ctx = dash.callback_context

    # Close modal logic: If the close button is clicked
    if ctx.triggered and 'close-modal' in ctx.triggered[0]['prop_id']:
        return None, {'display': 'none'}, None, {'display': 'none'}

    # Open modal logic: If the heatmap is clicked
    if clickData:
        full_path = os.path.join('public', "modal.html")
        html_content = None
        with open(full_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        clicked_point = clickData['points'][0]
        x = clicked_point['x']
        y = clicked_point['y']
        value = clicked_point['z']

        clean_label = re.sub(r"</?b>", "", y)

        figure_data = figure_map.get(x, {}).get(clean_html_string(y))

        if figure_data is None:
            return None, {'display': 'none'}, None, {'display': 'none'}
        figure = figure_data['figure']
        metadata = figure_data['metadata']

        modal_content = html.Div(
            style={
                'position': 'fixed',
                'top': '50%',
                'left': '50%',
                'transform': 'translate(-50%, -50%)',
                'zIndex': 1000,
                'backgroundColor': '#ffffff',
                'padding': '30px',
                'boxShadow': '0 8px 20px rgba(0, 0, 0, 0.3)',
                'borderRadius': '15px',
                'width': '75%',
                'height': "75%",
                'maxWidth': '1200px',
                'textAlign': 'center',
                'fontFamily': 'Arial, sans-serif',
                'direction': 'rtl',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'flex-start',  # Align content to the top
            },
            children=[
                # Close Button at the Top Right
                html.Button(
                    "×",  # Close icon
                    id={'type': 'close-modal', 'index': 0},
                    n_clicks=0,
                    style={
                        'position': 'absolute',
                        'top': '10px',
                        'right': '10px',
                        'backgroundColor': 'transparent',
                        'border': 'none',
                        'color': '#34495e',
                        'fontSize': '24px',
                        'fontWeight': 'bold',
                        'cursor': 'pointer',
                    }
                ),
                # Title
                html.H1(x + "," + clean_html_string(y), style={
                    'fontSize': '28px',
                    'fontWeight': 'bold',
                    'color': '#34495e',
                    'marginBottom': '10px',
                }),
                # Subtitle
                html.H3(metadata["survey_item"], style={
                    'fontSize': '20px',
                    'fontWeight': 'normal',
                    'color': '#7f8c8d',
                    "zIndex": 1000
                }),
                # Chart
                dcc.Graph(figure=figure, config={
                    'displayModeBar': False  # Disable the top-right menu
                },
                    style={'height': '100%', "marginTop": "-5%"}),
                html.P(metadata["notes"], style={
                    'fontSize': '16px',
                    'color': '#34495e',
                    'marginTop': '20px',
                    'textAlign': 'justify',
                }),
                # Link at the Bottom Right
                html.A(
                    "למידע נוסף לחץ כאן",
                    href=metadata["link"],
                    target="_blank",
                    style={
                        'position': 'absolute',
                        'bottom': '20px',
                        'right': '20px',
                        'color': '#1abc9c',
                        'fontSize': '16px',
                        'textDecoration': 'none',
                        'fontWeight': 'bold',
                    }
                )
            ]
        )

        return {
            'x': x,
            'y': y,
            'value': value
        }, {'display': 'block'}, modal_content, {'display': 'block'}  # Show overlay

@dashApp.callback(
    Output('heatmap-size', 'data'),
    [Input('increase-size-button', 'n_clicks'),
     Input('decrease-size-button', 'n_clicks')],
    State('heatmap-size', 'data')
)
def update_heatmap_size(increase_clicks, decrease_clicks, current_size):
    # Adjust heatmap size by 10% based on button clicks
    new_width = current_size['width']
    new_height = current_size['height']

    if dash.callback_context.triggered_id == 'increase-size-button' and increase_clicks > 0:
        new_width *= 1.1
        new_height *= 1.1
    elif dash.callback_context.triggered_id == 'decrease-size-button' and decrease_clicks > 0:
        new_width *= 0.9
        new_height *= 0.9

    return {'width': int(new_width), 'height': int(new_height)}

if __name__ == '__main__':
    app.run(debug=True, port=8051)
