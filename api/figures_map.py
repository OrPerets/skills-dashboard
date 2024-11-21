# import plotly.graph_objects as go
# import random
# import json

# with open("public/measurement_map.json", encoding="utf-8") as f:
#     data = json.load(f)

# rows = list(set(item['התנהגות / עמדות / ידע'] for item in data))
# columns = list(set(item['תחום'] for item in data))

# # Mockup data for scatter plot
# categories = ['Category A', 'Category B', 'Category C', 'Category D']
# x_values = [random.randint(1, 10) for _ in range(50)]  # Random X values
# y_values = [random.randint(10, 100) for _ in range(50)]  # Random Y values
# labels = [random.choice(categories) for _ in range(50)]  # Random categories as labels


# def generate_dynamic_figure(x, y):
#     # Mockup Data for Bar Chart
#     categories = ['Category A', 'Category B', 'Category C', 'Category D']
#     values = [10, 20, 15, 25]  # Mockup values
#     fig = go.Figure(data=[
#         go.Bar(
#             x=categories,
#             y=values,
#             marker_color='indianred',
#             width=0.8,
#         )
#     ])
#     fig.update_layout(
#         xaxis_title=x,
#         yaxis_title=y,
#         clickmode="event+select"
#     )
#     return fig

# def generate_scatter():
#     # Create scatter plot
#     fig = go.Figure()

#     fig.add_trace(
#         go.Scatter(
#             x=x_values,
#             y=y_values,
#             mode='markers',
#             marker=dict(
#                 size=10,           # Marker size
#                 color=y_values,    # Color by Y values
#                 colorscale='Viridis',
#                 showscale=True     # Show color scale
#             ),
#             text=labels,          # Labels for hover
#             hoverinfo='text+x+y'  # Info to show on hover
#         )
#     )

#     # Customize layout
#     fig.update_layout(
#         title="Mockup Scatter Plot",
#         xaxis_title="X Axis",
#         yaxis_title="Y Axis",
#         template="plotly_white",
#         clickmode="event+select"  # Enable click interactions
#     )

#     return fig 


# figure_map = {}

# # Populate figures_map with figures and metadata
# for item in data:
#     row = item['התנהגות / עמדות / ידע']
#     column = item['תחום']

#     # Prepare metadata for this (row, column)
#     metadata = {
#         'measurement_method': item.get('אופן חישוב המדד', 'Not Available'),
#         'survey_item': item.get('סעיף / היגד על', 'Not Available'),
#         'original_item': item.get('פריט/היגד מקורי', 'Not Available'),
#         'source': item.get('מקור', 'Not Available'),
#         'link': item.get('קישור', '#'),
#         'notes': item.get('הערות', 'None')
#     }

#     # Generate a placeholder figure (use scatter and bar alternately for example)
#     if "עמדות" in row:
#         figure = go.Figure(
#             data=go.Bar(
#                 x=columns,
#                 y=[5, 10, 15, 20, 25],  # Mock data for bar chart
#                 marker_color='indianred'
#             )
#         )
#         figure.update_layout(
#             title=f"Bar Chart for {row} - {column}",
#             xaxis_title="Categories",
#             yaxis_title="Values"
#         )
#     else:
#         figure = go.Figure(
#             data=go.Scatter(
#                 x=[1, 2, 3, 4, 5],  # Mock X values
#                 y=[10, 20, 30, 40, 50],  # Mock Y values
#                 mode='markers',
#                 marker=dict(size=10, color=[10, 20, 30, 40, 50], colorscale='Viridis')
#             )
#         )
#         figure.update_layout(
#             # title=f"Scatter Plot for {row} - {column}",
#             xaxis_title=row,
#             yaxis_title=column
#         )

#     # Store the figure and metadata in the dictionary
#     figure_map[(row, column)] = {
#         'figure': figure,
#         'metadata': metadata
#     }

def normalize_key(key):
    """Normalize keys to ensure consistency (e.g., trim spaces, unify cases)."""
    return tuple(str(x).strip() for x in key)

# # Normalize all keys in figures_map
# figure_map = {
#     normalize_key(k): v
#     for k, v in figure_map.items()
# }
import plotly.graph_objects as go
import random
import json

# Load the measurement data
with open("public/measurement_map.json", encoding="utf-8") as f:
    data = json.load(f)

# Heatmap rows and columns
rows = ['תעסוקה', 'בריאות', 'פיננסים', 'פנאי ובידור', 'למידה דיגיטאלית', 'מיצוי זכויות', 
        'חברה ותקשורת', 'צרכנות', 'ביטחון ובטיחות', 'כללי']
cols = ['ניהול מידע התנהגות', 'ניהול מידע עמדות', 'ניהול מידע ידע', 'תקשור התנהגות', 
        'תקשור עמדות', 'תקשור ידע', 'עסקאות התנהגות', 'עסקאות עמדות', 'עסקאות ידע', 
        'פתרון בעיות התנהגות', 'פתרון בעיות עמדות', 'פתרון בעיות ידע', 
        'תחומי חיים כללי התנהגות', 'תחומי חיים כללי עמדות', 'תחומי חיים כללי ידע', 
        'AI התנהגות', 'AI עמדות', 'AI ידע']

# Function to generate a mock bar chart
def generate_dynamic_figure(x, y):
    categories = ['Category A', 'Category B', 'Category C', 'Category D']
    values = [random.randint(5, 30) for _ in categories]
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color='indianred',
            width=0.8,
        )
    ])
    fig.update_layout(
        xaxis_title=x,
        yaxis_title=y
    )
    return fig

# Initialize figure_map
figure_map = {}

# Populate figure_map with figures and metadata
for row in rows:
    figure_map[row] = {}  # Nested dictionary for columns
    for col in cols:
        # Mock metadata
        metadata = {
            'measurement_method': f"Method for {row} - {col}",
            'survey_item': 'תת-כותרת',
            'source': "Mock Source",
            'link': "https://example.com",
            'notes': "These are example notes."
        }

        # Generate a dynamic figure
        figure = generate_dynamic_figure(row, col)

        # Store in the map
        figure_map[row][col] = {
            'figure': figure,
            'metadata': metadata
        }
