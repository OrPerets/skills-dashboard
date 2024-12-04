import plotly.graph_objects as go
import random
import json

def update_json_with_random(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:  # Ensure UTF-8 encoding for Hebrew
            data = json.load(f)

        for item in data:
            for key, value in item.items():
                if isinstance(value, int):  # Check if the value is an integer (numeric)
                    item[key] = random.randint(0, 10)

        with open(filepath, 'w', encoding='utf-8') as f:  # Overwrite the file
            json.dump(data, f, indent=4, ensure_ascii=False)  # Preserve Hebrew characters


    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



# Load the measurement data from JSON file
with open("public/measurement_map.json", encoding="utf-8") as f:
    data = json.load(f)
    for item in data:
            for key, value in item.items():
                if isinstance(value, int):  # Check if the value is an integer (numeric)
                    item[key] = random.randint(0, 10)


# Combine relevant columns for unique metric identification and prepare the data
data = [
    {
        **item,
        'combined_metric': item['מאפיין'] + " - " + item['התנהגות / עמדות / ידע']
    }
    for item in data
]

# Define the fixed rows and columns
rows = ['תעסוקה', 'בריאות', 'פיננסים', 'פנאי ובידור', 'למידה דיגיטאלית', 'מיצוי זכויות', 
        'חברה ותקשורת', 'צרכנות', 'ביטחון ובטיחות', 'כללי']
cols = ['ניהול מידע התנהגות', 'ניהול מידע עמדות', 'ניהול מידע ידע', 'תקשור התנהגות', 
        'תקשור עמדות', 'תקשור ידע', 'עסקאות התנהגות', 'עסקאות עמדות', 'עסקאות ידע', 
        'פתרון בעיות התנהגות', 'פתרון בעיות עמדות', 'פתרון בעיות ידע', 
        'תחומי חיים כללי התנהגות', 'תחומי חיים כללי עמדות', 'תחומי חיים כללי ידע', 
        'AI התנהגות', 'AI עמדות', 'AI ידע']

# Function to normalize keys to ensure consistency (e.g., trim spaces, unify cases)
def normalize_key(key):
    return tuple(str(x).strip() for x in key)

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
        yaxis_title=y,
        plot_bgcolor="rgba(248,249,250,1)",
        paper_bgcolor="rgba(248,249,250,1)",
    )
    return fig

# Initialize figure_map
dynamic_figure_map = {}

# Populate figure_map with figures and metadata
for row in rows:
    dynamic_figure_map[row] = {}
    for col in cols:
        # Filter the data for the current row and col combination
        filtered_data = [
            item for item in data
            if item['תחום'] == row and item['מאפיין'] + ' ' + item['התנהגות / עמדות / ידע'] == col
        ]
        
        # If there's data for this combination, generate figure and metadata
        if filtered_data:
            # Extracting data for metadata, with default values for missing data
            item = filtered_data[0]  # Use the first matching item
            metadata = {
                'measurement_method': item.get('אופן חישוב המדד', "N/A"),
                'survey_item': item.get('סעיף / היגד על', ""),
                'source': item.get('מקור', "U"),
                'link': item.get('קישור', ""),
                'notes': item.get('הערות', "")
            }

            # Generating a figure (mocked for now, but can be adjusted to use actual data)
            figure = generate_dynamic_figure(row, col)

            # Store in the map
            dynamic_figure_map[row][col] = {
                'figure': figure,
                'metadata': metadata
            }

# Replace original figure_map with dynamic_figure_map
figure_map = dynamic_figure_map