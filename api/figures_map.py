import plotly.graph_objects as go
import random
import json
import re

def extract_bracketed_values(text):
    """Extracts the values inside square brackets from a string.
    
    Args:
        text: The input string.

    Returns:
        A list of strings containing the bracketed values, or None if no brackets are found.
    """
    match = re.search(r"\[(.*?)\]", text)  # Non-greedy match to handle multiple brackets
    if match:
        values_string = match.group(1)
        values = [value.strip() for value in values_string.split(",")]
        return values
    else:
        return None  # Or return an empty list if you prefer: []


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
def generate_dynamic_figure(x, y, values):
    if values:
        categories = values
    else:
        categories = ['Category A', 'Category B', 'Category C', 'Category D']  # Default if no values
    values_counts = [random.randint(5, 30) for _ in categories] # Mock values
    fig = go.Figure(data=[
        go.Bar(
            x=categories,  # Use the provided values
            y=values_counts,
            marker_color='indianred',
            width=0.8,
        )
    ])
    fig.update_layout(  # ... (rest of layout code)
        xaxis_title = x, # for bar
        yaxis_title = y # for bar

    )
    return fig

def generate_pie_chart(x, y, values):  # Add 'values' as a parameter
    if values:
        labels = values
    else:
        labels = ['Section A', 'Section B', 'Section C', 'Section D'] # Default

    values_counts = [random.randint(5, 30) for _ in labels] # Mock data
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_counts, hole=.3)])
    fig.update_layout(  # ... (rest of layout code)
        #  title=f"{x} - {y}",  # Use x and y in the title

    )
    return fig



def generate_scatter_plot(x, y, values):
    if values:  # Use values if available, otherwise default to random values
        x_values = values
    else:
        x_values = [random.random() for _ in range(20)]
    
    y_values = [random.random() for _ in range(20)] # Mock data

    fig = go.Figure(data=go.Scatter(x=x_values, y=y_values, mode='markers')) # ...


    fig.update_layout( # ... rest of the code

        xaxis_title = x, #for scatter
        yaxis_title = y #for scatter
    )
    return fig




def generate_line_chart(x, y, values):
    if values:  # Use values if available, otherwise default to a range
        x_values = values
    else:
        x_values = list(range(10))

    y_values = [random.randint(10, 30) for _ in range(len(x_values))]  # Example y-values

    fig = go.Figure(data=go.Scatter(x=x_values, y=y_values, mode='lines+markers'))
    fig.update_layout(  # ... rest of layout
        xaxis_title = x, # for line
        yaxis_title = y # for line
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

            values = extract_bracketed_values(item.get("פריט/היגד מקורי", ""))


            if item.get("גרף", "") == "bar":
            # Generating a figure (mocked for now, but can be adjusted to use actual data)
                figure = generate_dynamic_figure(row, col, values)
            elif item.get("גרף", "") == "scatter":
                figure = generate_scatter_plot(row, col, values)
            elif item.get("גרף", "") == "line":
                figure = generate_line_chart(row, col, values)
            elif item.get("גרף", "") == "pie":
                figure = generate_pie_chart(row, col, values)
            else:
                figure = generate_dynamic_figure(row, col, values)

            # Store in the map
            dynamic_figure_map[row][col] = {
                'figure': figure,
                'metadata': metadata
            }

# Replace original figure_map with dynamic_figure_map
figure_map = dynamic_figure_map