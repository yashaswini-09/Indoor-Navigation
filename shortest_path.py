# @title
# Install libraries if needed
# !pip install networkx matplotlib ipywidgets

import networkx as nx
import matplotlib.pyplot as plt
from ipywidgets import interact, widgets, VBox, HBox, Output, Button
from IPython.display import display, clear_output

# -------------------------------
# Graph Setup
# -------------------------------
adjacency_list = {
    '201': ['213', '214', 'stairs1', '212'],
    '202': ['214', 'stairs1', '215', '203', '216'],
    '203': ['216', 'stairs5', '202', '215'],
    '204': ['205', '217', '218', 'stairs5', 'stairs6'],
    '205': ['stairs2', '219', '218', '204', '217'],
    '206': ['219', '220', 'stairs2'],
    '207': ['221', 'stairs2', '222', '220'],
    '208': ['222', '209', '223', 'stairs2'],
    '209': ['223', '222', '208', 'stairs7', 'stairs8'],
    '210': ['stairs8', '224', '211', '225', 'stairs7'],
    '211': ['210', '224', '225', '226', 'stairs4'],
    '212': ['stairs4', '226', '227', '201', '213'],
    '213': ['212', '201', 'stairs1', '214', '227'],
    '214': ['201', '202', 'stairs1', '215', '216'],
    '215': ['202', '203', '214', '216', 'stairs1'],
    '216': ['202', '203', '215', 'stairs5', 'stairs6'],
    '217': ['204', '205', '218', 'stairs6', 'stairs5'],
    '218': ['204', '205', '217', '219', 'stairs2'],
    '219': ['205', '206', 'stairs2', '220'],
    '220': ['206', '207', '221', '219'],
    '221': ['207', '220', 'stairs3', '222'],
    '222': ['207', '208', '209', '221', '223', 'stairs3'],
    '223': ['208', '209', 'stairs7', '222'],
    '224': ['210', '211', 'stairs8', '225'],
    '225': ['210', '211', 'stairs4', '224', '226'],
    '226': ['211', '212', '227', '225', 'stairs4'],
    '227': ['212', '226', 'stairs4', '213'],
    'stairs1': ['201', '202', '213', '214', '215'],
    'stairs2': ['205', '206', '219', '218'],
    'stairs3': ['207', '208', '221', '222'],
    'stairs4': ['211', '212', '225', '226', '227'],
    'stairs5': ['204', '203', '216', '217'],
    'stairs6': ['204', '203', '216', '217'],
    'stairs7': ['stairs8', '209', '210'],
    'stairs8': ['210', 'stairs7', '209']
}

G = nx.Graph()
for node, neighbors in adjacency_list.items():
    for neighbor in neighbors:
        G.add_edge(node, neighbor)

pos = nx.spring_layout(G, seed=42)

# -------------------------------
# UI Setup
# -------------------------------
nodes = list(G.nodes)
source_dropdown = widgets.Dropdown(options=nodes, description='Source:')
destination_dropdown = widgets.Dropdown(options=nodes, description='Destination:')
start_button = Button(description="Start Tracking", button_style='success')
next_button = Button(description="Next Step", button_style='primary', disabled=True)
output_area = Output()

movement_state = {
    "path": [],
    "current_index": 0,
    "history": [],
    "destination": None
}

# -------------------------------
# Graph Drawing Function
# -------------------------------
def draw_progress_graph():
    plt.figure(figsize=(18, 12))
    plt.title("Indoor Navigation - Live Movement", fontsize=18)
    plt.gca().set_facecolor('#f0f0f0')

    stair_nodes = [node for node in G.nodes if 'stairs' in node]
    normal_nodes = [node for node in G.nodes if 'stairs' not in node]

    # Edges
    nx.draw_networkx_edges(G, pos, edge_color='gray', width=2, alpha=0.4)

    # Full path
    path = movement_state["path"]
    path_edges = list(zip(path[:-1], path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=3)

    # Nodes
    visited = movement_state["history"][:-1]
    current = movement_state["history"][-1] if movement_state["history"] else None

    nx.draw_networkx_nodes(G, pos, nodelist=normal_nodes, node_color='skyblue', node_size=800, edgecolors='black')
    nx.draw_networkx_nodes(G, pos, nodelist=stair_nodes, node_color='lightgreen', node_size=800, edgecolors='black')
    nx.draw_networkx_nodes(G, pos, nodelist=visited, node_color='green', node_size=900, edgecolors='black')

    if current:
        nx.draw_networkx_nodes(G, pos, nodelist=[current], node_color='blue', node_size=1000, edgecolors='black')
    if movement_state["destination"]:
        nx.draw_networkx_nodes(G, pos, nodelist=[movement_state["destination"]], node_color='red', node_size=1000, edgecolors='black')

    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')
    plt.axis('off')
    plt.show()

# -------------------------------
# Button Functions
# -------------------------------
def on_start_click(b):
    src = source_dropdown.value
    dst = destination_dropdown.value
    try:
        path = nx.shortest_path(G, source=src, target=dst)
        movement_state.update({
            "path": path,
            "current_index": 0,
            "history": [],
            "destination": dst
        })
        next_button.disabled = False
        with output_area:
            clear_output()
            print(f"Tracking started from {src} to {dst}")
        draw_progress_graph()
    except nx.NetworkXNoPath:
        with output_area:
            clear_output()
            print("No path found!")

def on_next_click(b):
    if movement_state["current_index"] < len(movement_state["path"]):
        node = movement_state["path"][movement_state["current_index"]]
        movement_state["history"].append(node)
        movement_state["current_index"] += 1

        with output_area:
            clear_output()
            print(f"Step {movement_state['current_index']}/{len(movement_state['path'])}")
            print(f"Moved to: {node}")
        draw_progress_graph()
    else:
        with output_area:
            clear_output()
            print("Reached destination.")
            print(f"Full path: {movement_state['path']}")

# Connect buttons to functions
start_button.on_click(on_start_click)
next_button.on_click(on_next_click)

# Display UI
ui = VBox([HBox([source_dropdown, destination_dropdown]), HBox([start_button, next_button]), output_area])
display(ui)