import tkinter as tk
from tkinter import ttk
import networkx as nx
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from collections import Counter
from itertools import combinations, groupby, product
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from ortools.linear_solver import pywraplp
import time
import webbrowser
from ttkthemes import ThemedTk


global_graph = None

fig1 = None
fig2 = None
fig3 = None
fig4 = None
fig5 = None

global node_entry



def open_link():
    webbrowser.open("https://www.mdpi.com/2227-7390/10/4/640#:~:text=The%20domatic%20partition%20problem%20consists,proved%20to%20be%20NP%2Dcomplete.")

def clear_canvas(canvas_frame):
    for widget in canvas_frame.winfo_children():
        widget.destroy()


def open_algorithm_screen(algorithm):
    if algorithm in ["Exhaustive Search"]:
        open_exhaustive_screen(algorithm)
    if algorithm in ["Heuristic"]:
        open__heuristic_screen(algorithm)
    if algorithm in ["Allied Domination"]:
        open_allied_domination_screen(algorithm)
    
        
def open__heuristic_screen(algorithm):
    
    global node_entry

    new_window = tk.Toplevel(root)
    new_window.title(algorithm + " Algorithm")
    new_window.geometry("950x600")
    new_window.configure(bg='#115982')

    left_frame = tk.Frame(new_window)
    left_frame.pack(side="left", fill="y", padx=70, pady=10)
    left_frame.configure(bg='#115982')

    tk.Label(left_frame, text="Enter Number of Nodes:",bg='#115982').pack(pady=(20,0))
    node_entry = tk.Entry(left_frame)
    node_entry.pack(pady=5)
    
    tk.Label(left_frame, text="Select Density:", bg='#115982').pack(pady=(5,0))
    density_frame = tk.Frame(left_frame, bg='#115982')
    density_frame.pack(pady=(0,15))
    density_var = tk.DoubleVar(new_window)
    densities = [0.2, 0.4, 0.6, 0.8, 1.0]
    for density in densities:
        tk.Radiobutton(density_frame, text=str(density), variable=density_var, value=density, bg='#115982').pack(side=tk.LEFT)

    density_var.set(0.2)
    
    generate_graph_button = tk.Button(left_frame, text="Generate Graph", command=lambda: generate_graph(node_entry.get(),density_var.get()))
    generate_graph_button.pack(pady=5)
    generate_custom_graph_button = tk.Button(left_frame, text="Sample Graph", command=lambda: generate_custom_graph(node_entry.get()))
    generate_custom_graph_button.pack(pady=5)
    run_algorithm_button = tk.Button(left_frame, text="Run Algorithm", state="disabled", command=lambda: run_algorithm(node_entry.get(),density_var.get()))
    run_algorithm_button.pack(pady=(0,50))
    

    right_frame = tk.Frame(new_window)
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    right_frame.configure(bg='#115982')

    input_graph_frame = tk.Frame(right_frame)
    input_graph_frame.pack(fill="both", expand=True)
    input_graph_frame.configure(bg='#115982')
    tk.Label(input_graph_frame, text="Input Graph",bg='#115982').pack()
    input_graph = tk.Canvas(input_graph_frame, bg="white", width=400, height=200)  # Sabit boyutlar
    input_graph.pack()
    
    # Output Graph 
    output_graph_frame = tk.Frame(right_frame)
    output_graph_frame.pack(fill="both", expand=True)
    output_graph_frame.configure(bg='#115982')
    tk.Label(output_graph_frame, text="Output Graph",bg='#115982').pack()
    output_graph = tk.Canvas(output_graph_frame, bg="white", width=400, height=200)  # Sabit boyutlar
    output_graph.pack()
    
    # Log 
    log_label = tk.Label(left_frame, text="Algorithm Run Log", bg='#115982')
    log_label.pack()
    # Log  Listbox
    log_listbox = tk.Listbox(left_frame, height=15, width=33)
    log_listbox.pack(pady=10)


    def generate_graph(nodes,density):
        clear_canvas(input_graph)

        global global_graph

        def generate_random_connected_separable_graph(node_count, density):
            if node_count <= 1:
                return nx.complete_graph(node_count)

            G = nx.Graph()
            G.add_nodes_from(range(node_count))

            remaining_nodes = set(G.nodes())
            while remaining_nodes:
                size = random.randint(1, min(len(remaining_nodes), node_count // 2))
                subgraph_nodes = random.sample(list(remaining_nodes), size)

                subgraph = nx.Graph()
                subgraph.add_nodes_from(subgraph_nodes)
                if size > 1:
                    max_edges = size * (size - 1) // 2
                    edges_to_add = int(max_edges * density)
                    while subgraph.number_of_edges() < edges_to_add:
                        u, v = random.sample(subgraph_nodes, 2)
                        subgraph.add_edge(u, v)

                if len(G.edges()) > 0: 
                    connect_node = random.choice(list(subgraph_nodes))
                    node_to_connect = random.choice(list(G.nodes() - set(subgraph_nodes)))
                    subgraph.add_edge(connect_node, node_to_connect)

                G = nx.compose(G, subgraph)
                remaining_nodes -= set(subgraph_nodes)

            components = list(nx.connected_components(G))
            while len(components) > 1:
                # Connect two components
                u = random.choice(list(components[0]))
                v = random.choice(list(components[1]))
                G.add_edge(u, v)
                components = list(nx.connected_components(G))

            return G
        
        G = generate_random_connected_separable_graph(int(nodes),density)
        global_graph = G
        fig = plt.figure(figsize=(6, 3))
        nx.draw(G, with_labels=True)
        plt.title("Input Graph G")

        canvas = FigureCanvasTkAgg(fig, master=input_graph)  # input_graph_frame
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True) 
        
        run_algorithm_button['state'] = "normal"
    
    def generate_custom_graph(nodes):
        clear_canvas(input_graph)

        global global_graph
        
        global node_entry


        def custom_graph(G):
            # Özel kenar listesi tanımlayın.
            specific_edges = [(0, 1), (0, 2), (0, 6), (1, 2), (1, 6), (6, 2), (2, 3), (3, 7), (3, 4), (7, 4), (7, 8), (4, 8), (8, 5), (8, 9), (5, 9)]

            # En büyük düğüm numarasına göre düğümleri ekleyin.
            max_node = max(max(edge) for edge in specific_edges)
            G.add_nodes_from(range(max_node + 1), color='')

            # Belirtilen kenarları ekleyin.
            G.add_edges_from(specific_edges)

            return G
        
        G = nx.Graph()
        global_graph = custom_graph(G)
        fig = plt.figure(figsize=(6, 3))
        nx.draw(G, with_labels=True)
        plt.title("Input Graph G")

        canvas = FigureCanvasTkAgg(fig, master=input_graph)  # input_graph_frame
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True) 
        
        node_entry.delete(0, tk.END)
        node_entry.insert(0, "10")
        
        run_algorithm_button['state'] = "normal"

    def run_algorithm(nodes,density):
        clear_canvas(output_graph)

        global global_graph
        
        def heuristic_domatic_partition(G):
            nodes_sorted_by_degree = sorted(G.nodes(), key=lambda x: len(G[x]), reverse=True)
            
            node_colors = {node: None for node in G.nodes()}

            for node in nodes_sorted_by_degree:
                adjacent_colors = set(node_colors[neighbor] for neighbor in G[node] if node_colors[neighbor] is not None)
                available_colors = set(range(len(G))) - adjacent_colors

                if not available_colors:
                    node_colors[node] = max(node_colors.values()) + 1
                else:
                    node_colors[node] = min(available_colors)

            for node in nodes_sorted_by_degree:
                for color in range(max(node_colors.values())):
                    if all(node_colors[neighbor] != color for neighbor in G[node]):
                        node_colors[node] = color
                        break

            for node, color in node_colors.items():
                G.nodes[node]['color'] = color

            return G
        
        start_time = time.time() 
        
        colored_graph = heuristic_domatic_partition(global_graph)
        
        fig = plt.figure(figsize=(6, 3))
        nx.draw(colored_graph, with_labels=True, node_color=[color for _, color in nx.get_node_attributes(colored_graph, 'color').items()])
        plt.title("Domatic Partition G")
        
        end_time = time.time()  # Algoritmanın bitiş zamanı
        run_time = round(end_time - start_time, 2)  # Çalışma süresi
        log_listbox.insert(tk.END, f"Nodes: {nodes}       Density: {density}       Run time: {run_time} s")
        
        canvas = FigureCanvasTkAgg(fig, master=output_graph)  # input_graph_frame
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True) 
        

def open_exhaustive_screen(algorithm):
    global node_entry

    new_window = tk.Toplevel(root)
    new_window.title(algorithm + " Algorithm")
    new_window.geometry("950x600")
    new_window.configure(bg='#115982')


    left_frame = tk.Frame(new_window)
    left_frame.pack(side="left", fill="y", padx=70, pady=10)
    left_frame.configure(bg='#115982')


    tk.Label(left_frame, text="Enter Number of Nodes:",bg='#115982').pack(pady=(20,0))
    node_entry = tk.Entry(left_frame)
    node_entry.pack(pady=5)
    
    tk.Label(left_frame, text="Select Density:", bg='#115982').pack(pady=(5,0))
    density_frame = tk.Frame(left_frame, bg='#115982')
    density_frame.pack(pady=(0,15))
    density_var = tk.DoubleVar(new_window)
    densities = [0.2, 0.4, 0.6, 0.8, 1.0]
    for density in densities:
        tk.Radiobutton(density_frame, text=str(density), variable=density_var, value=density, bg='#115982').pack(side=tk.LEFT)

    density_var.set(0.2)
    
    generate_graph_button = tk.Button(left_frame, text="Generate Graph", command=lambda: generate_graph(node_entry.get(),density_var.get()))
    generate_graph_button.pack(pady=5)
    generate_custom_graph_button = tk.Button(left_frame, text="Sample Graph", command=lambda: generate_custom_graph(node_entry.get()))
    generate_custom_graph_button.pack(pady=5)
    run_algorithm_button = tk.Button(left_frame, text="Run Algorithm", state="disabled", command=lambda: run_algorithm(node_entry.get(),density_var.get()))
    run_algorithm_button.pack(pady=(0,50))

    right_frame = tk.Frame(new_window)
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    right_frame.configure(bg='#115982')


    input_graph_frame = tk.Frame(right_frame)
    input_graph_frame.pack(fill="both", expand=True)
    input_graph_frame.configure(bg='#115982')
    tk.Label(input_graph_frame, text="Input Graph",bg='#115982').pack()
    input_graph = tk.Canvas(input_graph_frame, bg="white", width=400, height=200)  # Sabit boyutlar
    input_graph.pack()
    
    output_graph_frame = tk.Frame(right_frame)
    output_graph_frame.pack(fill="both", expand=True)
    output_graph_frame.configure(bg='#115982')
    tk.Label(output_graph_frame, text="Output Graph",bg='#115982').pack()
    output_graph = tk.Canvas(output_graph_frame, bg="white", width=400, height=200)  # Sabit boyutlar
    output_graph.pack()
    
    log_label = tk.Label(left_frame, text="Algorithm Run Log", bg='#115982')
    log_label.pack()
    log_listbox = tk.Listbox(left_frame, height=15, width=33)
    log_listbox.pack(pady=10)

    def generate_graph(nodes,density):
        clear_canvas(input_graph)

        global global_graph

        def generate_random_connected_separable_graph(node_count, density):
            if node_count <= 1:
                return nx.complete_graph(node_count)

            G = nx.Graph()
            G.add_nodes_from(range(node_count))

            remaining_nodes = set(G.nodes())
            while remaining_nodes:
                size = random.randint(1, min(len(remaining_nodes), node_count // 2))
                subgraph_nodes = random.sample(list(remaining_nodes), size)

                subgraph = nx.Graph()
                subgraph.add_nodes_from(subgraph_nodes)
                if size > 1:
                    max_edges = size * (size - 1) // 2
                    edges_to_add = int(max_edges * density)
                    while subgraph.number_of_edges() < edges_to_add:
                        u, v = random.sample(subgraph_nodes, 2)
                        subgraph.add_edge(u, v)

                if len(G.edges()) > 0: 
                    connect_node = random.choice(list(subgraph_nodes))
                    node_to_connect = random.choice(list(G.nodes() - set(subgraph_nodes)))
                    subgraph.add_edge(connect_node, node_to_connect)

                G = nx.compose(G, subgraph)
                remaining_nodes -= set(subgraph_nodes)

            components = list(nx.connected_components(G))
            while len(components) > 1:
                u = random.choice(list(components[0]))
                v = random.choice(list(components[1]))
                G.add_edge(u, v)
                components = list(nx.connected_components(G))

            return G
        
        G = generate_random_connected_separable_graph(int(nodes),density)
        global_graph = G
        fig = plt.figure(figsize=(6, 3))
        nx.draw(G, with_labels=True)
        plt.title("Input Graph G")

        canvas = FigureCanvasTkAgg(fig, master=input_graph)  # input_graph_frame
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True) 
        
        run_algorithm_button['state'] = "normal"
        
    def generate_custom_graph(nodes):
        clear_canvas(input_graph)

        global global_graph
        global node_entry


        def custom_graph(G):
            specific_edges = [(0, 1), (0, 2), (0, 6), (1, 2), (1, 6), (6, 2), (2, 3), (3, 7), (3, 4), (7, 4), (7, 8), (4, 8), (8, 5), (8, 9), (5, 9)]

            max_node = max(max(edge) for edge in specific_edges)
            G.add_nodes_from(range(max_node + 1), color='')

            G.add_edges_from(specific_edges)

            return G
        
        G = nx.Graph()
        global_graph = custom_graph(G)
        fig = plt.figure(figsize=(6, 3))
        nx.draw(G, with_labels=True)
        plt.title("Input Graph G")

        canvas = FigureCanvasTkAgg(fig, master=input_graph)  # input_graph_frame, grafiğin gösterileceği yer
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        node_entry.delete(0, tk.END)
        node_entry.insert(0, "10")
        
        run_algorithm_button['state'] = "normal"

    def run_algorithm(nodes,density):
        clear_canvas(output_graph)

        global global_graph
        
        def isDomaticPartition(G,colorMap): 
          colors = []
          for i in G.nodes:
            G.nodes[i]['color'] = colorMap[i]
          for x in G.nodes:
            if G.nodes[x]['color'] not in colors:
              colors.append(G.nodes[x]['color'])
          for i in G.nodes:
            colorChecker = colors.copy()
            colorChecker.remove(G.nodes[i]['color'])
            for j in G.adj[i]:
              if G.nodes[j]['color'] in colorChecker:
                colorChecker.remove(G.nodes[j]['color'])
            if len(colorChecker) != 0:
              return False
          return True
      
        def findDomaticPartitions(graph,isEqualPartition):
          minDegree = len(graph.nodes)
          global dAllPart
          for i in graph.nodes:
            if minDegree > len(graph.adj[i]):
              minDegree = len(graph.adj[i])
          coloringProducts = product(range(1,minDegree+2),repeat=len(graph.nodes))
          totalColorings = list(coloringProducts)
          allColors = list(range(1,minDegree+2))
          dPart = {}
          dPartTemp = {}
          dPartEqual = {}
          for color in allColors:
            dPartTemp[color] = []
            dPart[color] = []
            dPartEqual[color] = []
          for possibleColoring in totalColorings:
            for color in allColors:
              if color not in possibleColoring:
                if max(possibleColoring) == color - 1:
                  dPartTemp[color - 1].append(possibleColoring)
                break
              if color == minDegree + 1:
                dPartTemp[minDegree+1].append(possibleColoring)
          for domaticSet, domaticColorings in dPartTemp.items():
            for validColoring in domaticColorings:
              if isDomaticPartition(graph,validColoring):
                dPart[domaticSet].append(validColoring)
          dAllPart = dPart
          if isEqualPartition:
            for domaticSet, domaticColorings in dPart.items():
              for validColoring in domaticColorings:
                if isEquitable(validColoring):
                  dPartEqual[domaticSet].append(validColoring)
            return dPartEqual
          else:
            return dPart
        
        def isEquitable(coloring):
          count = list(Counter(coloring).values())
          max = count[0]
          min = count[-1]
          if abs(min - max) > 1:
            return False
          return True
      
        def colorConvert(partition):
          colorMap = []
          for i in partition:
            colorMap.append(colors[i])
          return colorMap
      
        def Remove(tuples):
            tuples = [t for t in tuples if t]
            return tuples
        
        start_time = time.time() 
        
        colors = list(mcolors.get_named_colors_mapping().keys())

        dPartEqual = findDomaticPartitions(global_graph,True)
        dPartEqualasList = Remove(list(dPartEqual.values()))
        
        dPart = dAllPart
        dPartasList = Remove(list(dPart.values()))

        domaticNumber = max(dPartasList[-1][-1])
        equitableDomaticNumber = max(dPartasList[-1][-1])
        color_map = colorConvert(dPartEqualasList[-1][-1])
        """
        print("---------------------------------------------")
        print("Partition shown in the image: ",dPartEqualasList[-1][-1])
        print("domatic number: ",domaticNumber)
        print("equitable domatic number: ",equitableDomaticNumber)
        """
        fig = plt.figure(figsize=(6,3))
        nx.draw(global_graph, node_color=color_map ,with_labels=True)
        plt.title("Domatic Partition G")
        
        end_time = time.time()  # Algoritmanın bitiş zamanı
        run_time = round(end_time - start_time, 2)  # Çalışma süresi
        log_listbox.insert(tk.END, f"Nodes: {nodes}       Density: {density}       Run time: {run_time} s")
        
        canvas = FigureCanvasTkAgg(fig, master=output_graph)  # input_graph_frame
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True) 
        
        
def open_allied_domination_screen(algorithm):
    
    global node_entry
    
    new_window = tk.Toplevel(root)
    new_window.title(algorithm + " Algorithm")
    new_window.geometry("950x600")
    new_window.configure(bg='#115982')

    left_frame = tk.Frame(new_window, bg='#115982')
    left_frame.pack(side="left", fill="y", padx=10, pady=10)

    tk.Label(left_frame, text="Enter Number of Nodes:", bg='#115982').pack(pady=(20,0))
    node_entry = tk.Entry(left_frame)
    node_entry.pack(pady=5)
    
    tk.Label(left_frame, text="Select Density:", bg='#115982').pack(pady=(5,0))
    density_frame = tk.Frame(left_frame, bg='#115982')
    density_frame.pack(pady=(0,15))
    density_var = tk.DoubleVar(new_window)
    densities = [0.2, 0.4, 0.6, 0.8, 1.0]
    for density in densities:
        tk.Radiobutton(density_frame, text=str(density), variable=density_var, value=density, bg='#115982').pack(side=tk.LEFT)

    density_var.set(0.2)
    
    generate_graph_button = tk.Button(left_frame, text="Generate Graph", command=lambda: generate_graph(node_entry.get(),density_var.get()))
    generate_graph_button.pack(pady=5)
    generate_custom_graph_button = tk.Button(left_frame, text="Sample Graph", command=lambda: generate_custom_graph(node_entry.get()))
    generate_custom_graph_button.pack(pady=5)
    run_algorithm_button = tk.Button(left_frame, text="Run Algorithm", state="disabled", command=lambda: run_algorithm(node_entry.get(),density_var.get()))
    run_algorithm_button.pack(pady=5)
    show_steps_button = tk.Button(left_frame, text="Show Algorithm Steps", state="disabled", command=lambda: show_algorithm_steps())
    show_steps_button.pack(pady=(0,50))

    right_frame = tk.Frame(new_window, bg='#115982')
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    input_graph_frame = tk.Frame(right_frame, bg='#115982')
    input_graph_frame.pack(fill="both", expand=True)
    tk.Label(input_graph_frame, text="Input Graph", bg='#115982').pack()
    input_graph = tk.Canvas(input_graph_frame, bg="white", width=400, height=200)
    input_graph.pack()

    output_graph_frame = tk.Frame(right_frame, bg='#115982')
    output_graph_frame.pack(fill="both", expand=True)
    tk.Label(output_graph_frame, text="Output Graph", bg='#115982').pack()
    output_graph = tk.Canvas(output_graph_frame, bg="white", width=400, height=200)
    output_graph.pack()
    
    log_label = tk.Label(left_frame, text="Algorithm Run Log", bg='#115982')
    log_label.pack()
    log_listbox = tk.Listbox(left_frame, height=15, width=33)
    log_listbox.pack(pady=10)
    
    bottom_frame = tk.Frame(right_frame)
    bottom_frame.pack(side="bottom")
    
    link_label = tk.Label(bottom_frame, text="Visit MDPI Website : The Domatic Partition Problem in Separable Graphs", fg="blue",bg="white",font=("Helvetica", 12, "bold"), cursor="hand2")
    link_label.pack(side="left")  
    link_label.bind("<Button-1>", lambda e: open_link())

    def show_algorithm_steps():
        global fig1
        global fig2
        global fig3
        global fig4
        global fig5
        
        steps_window = tk.Toplevel(new_window)
        steps_window.title("Algorithm Steps")
        steps_window.geometry("1000x800")
        steps_window.configure(bg='#115982')

        left_frame = tk.Frame(steps_window, bg='#115982')
        left_frame.pack(side="left", fill="both", expand=True)

        step1_frame = tk.Frame(left_frame, bg='#115982')
        step1_frame.pack(fill="both", expand=True)
        tk.Label(step1_frame, text="Input Graph", bg='#115982').pack()
        step1 = tk.Canvas(step1_frame, bg="white", width=400, height=200)
        step1.pack()
        
        canvas = FigureCanvasTkAgg(fig1,master=step1)  
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        step2_frame = tk.Frame(left_frame, bg='#115982')
        step2_frame.pack(fill="both", expand=True)
        tk.Label(step2_frame, text="Block Decomposition", bg='#115982').pack()
        step2 = tk.Canvas(step2_frame, bg="white", width=400, height=200)
        step2.pack()
        
        #add to canvas
        canvas = FigureCanvasTkAgg(fig2,master=step2)  
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True) 

        step3_frame = tk.Frame(left_frame, bg='#115982')
        step3_frame.pack(fill="both", expand=True)
        tk.Label(step3_frame, text="Augmented Blocks", bg='#115982').pack()
        step3 = tk.Canvas(step3_frame, bg="white", width=400, height=200)
        step3.pack()
        
        canvas = FigureCanvasTkAgg(fig3,master=step3)  
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(steps_window, bg='#115982')
        right_frame.pack(side="right", fill="both", expand=True)

        step4_frame = tk.Frame(right_frame, bg='#115982')
        step4_frame.pack(fill="both", expand=True)
        tk.Label(step4_frame, text="Augmented Blocks Domatic Partition", bg='#115982').pack()
        step4 = tk.Canvas(step4_frame, bg="white", width=400, height=200)
        step4.pack()
        
        canvas = FigureCanvasTkAgg(fig4,master=step4)  
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        step5_frame = tk.Frame(right_frame, bg='#115982')
        step5_frame.pack(fill="both", expand=True)
        tk.Label(step5_frame, text="Combined Domatic Partition of the Input Graph", bg='#115982').pack()
        step5 = tk.Canvas(step5_frame, bg="white", width=400, height=200)
        step5.pack()
        
        canvas = FigureCanvasTkAgg(fig5,master=step5)  
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
    def generate_graph(nodes,density):
        clear_canvas(input_graph)

        global global_graph
        global fig1

        def generate_random_connected_separable_graph(node_count, density):
            if node_count <= 1:
                return nx.complete_graph(node_count)

            G = nx.Graph()
            G.add_nodes_from(range(node_count))

            remaining_nodes = set(G.nodes())
            while remaining_nodes:
                size = random.randint(1, min(len(remaining_nodes), node_count // 2))
                subgraph_nodes = random.sample(list(remaining_nodes), size)

                subgraph = nx.Graph()
                subgraph.add_nodes_from(subgraph_nodes)
                if size > 1:
                    max_edges = size * (size - 1) // 2
                    edges_to_add = int(max_edges * density)
                    while subgraph.number_of_edges() < edges_to_add:
                        u, v = random.sample(subgraph_nodes, 2)
                        subgraph.add_edge(u, v)

                if len(G.edges()) > 0: 
                    connect_node = random.choice(list(subgraph_nodes))
                    node_to_connect = random.choice(list(G.nodes() - set(subgraph_nodes)))
                    subgraph.add_edge(connect_node, node_to_connect)

                G = nx.compose(G, subgraph)
                remaining_nodes -= set(subgraph_nodes)

            components = list(nx.connected_components(G))
            while len(components) > 1:
                # Connect two components
                u = random.choice(list(components[0]))
                v = random.choice(list(components[1]))
                G.add_edge(u, v)
                components = list(nx.connected_components(G))

            return G
        
        G = generate_random_connected_separable_graph(int(nodes),density)
        global_graph = G
        fig = plt.figure(figsize=(6, 3))
        fig1 = fig
        nx.draw(G, with_labels=True)
        plt.title("Input Graph G")

        canvas = FigureCanvasTkAgg(fig, master=input_graph)  # input_graph_frame, grafiğin gösterileceği yer
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True) 
        
        run_algorithm_button['state'] = "normal"
        
        
    def generate_custom_graph(nodes):
        clear_canvas(input_graph)

        global global_graph
        global fig1
        global node_entry

        def custom_graph(G):
            specific_edges = [(0, 1), (0, 2), (0, 6), (1, 2), (1, 6), (6, 2), (2, 3), (3, 7), (3, 4), (7, 4), (7, 8), (4, 8), (8, 5), (8, 9), (5, 9)]

            max_node = max(max(edge) for edge in specific_edges)
            G.add_nodes_from(range(max_node + 1), color='')

            G.add_edges_from(specific_edges)

            return G
        
        G = nx.Graph()
        global_graph = custom_graph(G)
        fig = plt.figure(figsize=(6, 3))
        fig1 = fig
        nx.draw(G, with_labels=True)
        plt.title("Input Graph G")

        canvas = FigureCanvasTkAgg(fig, master=input_graph)  # input_graph_frame, grafiğin gösterileceği yer
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True) 
        
        node_entry.delete(0, tk.END)
        node_entry.insert(0, "10")
        
        run_algorithm_button['state'] = "normal"

    def run_algorithm(nodes, density):
        clear_canvas(output_graph)

        global global_graph
        global fig1
        global fig2
        global fig3
        global fig4
        global fig5
        
        def identify_blocks(G):
            blocks = list(nx.biconnected_components(G))
            block_graphs = [G.subgraph(block).copy() for block in blocks]
            return block_graphs

        def augment_blocks(blocks, G):
            augmented_blocks = []
            for block in blocks:
                neighbors = set()
                for node in block:
                    for neighbor in G.neighbors(node):
                        if neighbor not in block:
                            neighbors.add(neighbor)
                
                augmented_block = block.copy()
                augmented_block.add_nodes_from(neighbors)
                for neighbor in neighbors:
                    for edge in G.edges(neighbor):
                        if edge[1] in block or edge[0] in block:
                            augmented_block.add_edge(*edge)
                
                augmented_blocks.append(augmented_block)
            
            return augmented_blocks


        def find_domatic_partition(graph):
            solver = pywraplp.Solver.CreateSolver('SCIP')
            if not solver:
                solver = pywraplp.Solver.CreateSolver('CBC')
            if not solver:
                raise Exception("LP solver not available")

            nodes = list(graph.nodes)
            colors = list(range(1, len(nodes) + 1))
            x = {}
            for node in nodes:
                for color in colors:
                    x[(node, color)] = solver.IntVar(0, 1, f'x_{node}_{color}')

            for node in nodes:
                solver.Add(solver.Sum(x[(node, color)] for color in colors) == 1)

            for edge in graph.edges:
                for color in colors:
                    solver.Add(x[(edge[0], color)] + x[(edge[1], color)] <= 1)

            solver.Add(solver.Sum(x[(node, color)] for node in nodes for color in colors) == len(nodes))

            solver.Minimize(0) 

            solver.Solve()

            domatic_partition = []
            for node in nodes:
                for color in colors:
                    if x[(node, color)].solution_value() == 1:
                        domatic_partition.append((node, color))

            return domatic_partition
        
        start_time = time.time() 
        # Blokları tanımlama ve genişletme
        blocks = identify_blocks(global_graph)
        augmented_blocks = augment_blocks(blocks, global_graph)

        # Her arttırılmış blok için domatic partition çözme ve en iyi çözümü seçme
        best_partitions = []
        for block in augmented_blocks:
            domatic_partition = find_domatic_partition(block)
            best_partitions.append(domatic_partition)

        # Tüm çözümleri birleştirme
        final_solution = {}
        for partition in best_partitions:
            for node, color in partition:
                final_solution[node] = color
        
        end_time = time.time()  # Algoritmanın bitiş zamanı
        run_time = round(end_time - start_time, 2)  # Çalışma süresi
        log_listbox.insert(tk.END, f"Nodes: {nodes}       Density: {density}       Run time: {run_time} s")

        # Adım 2: Blok Dekompozisyonunun Görselleştirilmesi
        fig2, axes = plt.subplots(1, len(blocks), figsize=(6, 3))
        if len(blocks) == 1:  # Eğer sadece bir blok varsa
            axes = [axes]
        for i, block in enumerate(blocks):
            nx.draw(global_graph.subgraph(block), ax=axes[i], with_labels=True)
            axes[i].set_title(f"Block {i + 1}")

        # Adım 3: Genişletilmiş Blokların Görselleştirilmesi
        fig3, axes = plt.subplots(1, len(augmented_blocks), figsize=(6, 3))
        if len(augmented_blocks) == 1:  # Eğer sadece bir blok varsa
            axes = [axes]
        for i, block in enumerate(augmented_blocks):
            nx.draw(block, ax=axes[i], with_labels=True)
            axes[i].set_title(f"Block {i + 1}")

        # Adım 4: Genişletilmiş Bloklar için Domatic Partition'ın Görselleştirilmesi
        fig4, axes = plt.subplots(1, len(augmented_blocks), figsize=(6, 3))
        if len(augmented_blocks) == 1:  # Eğer sadece bir blok varsa
            axes = [axes]
        for i, (block, partition) in enumerate(zip(augmented_blocks, best_partitions)):
            color_map = [next(color for node, color in partition if node == n) for n in block.nodes()]
            nx.draw(block, ax=axes[i], node_color=color_map, with_labels=True, cmap=plt.cm.Set3)
            axes[i].set_title(f"Block {i + 1}")

        # Adım 5: Tüm Grafiğin Kombine Edilmiş Domatic Partition'ının Görselleştirilmesi
        fig5 = plt.figure(figsize=(6, 3))
        color_map = [final_solution.get(node, 0) for node in global_graph.nodes()]
        nx.draw(global_graph, node_color=color_map, with_labels=True, cmap=plt.cm.Set3)
        plt.title("Combined Domatic Partition of the Input Graph")
        
        
        canvas = FigureCanvasTkAgg(fig5, master=output_graph)  
        widget = canvas.get_tk_widget()
        widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True) 
        
        show_steps_button['state'] = "normal"
        
        
        
# Ana Ekran
root = tk.Tk()
root.title("Domatic Partition Algorithms")
root.configure(bg='#115982')


root.geometry("950x600") 


title_label = tk.Label(root, text="CSE 495 Graduation Project", font=("Helvetica", 25),bg='#115982')
title_label.pack(pady=(60,10))

title_label = tk.Label(root, text="Maximum Domatic Partition Problem", font=("Helvetica", 30,"bold"),bg='#115982')
title_label.pack(pady=(10,10))

title_label = tk.Label(root, text="Hikmet Mete Varol\n1801042608", font=("Helvetica", 15),bg='#115982')
title_label.pack(pady=10)

image_path = "graph.png" 
original_image = Image.open(image_path)
new_size = (150, 150)  
resized_image = original_image.resize(new_size)
photo = ImageTk.PhotoImage(resized_image)

image_label = tk.Label(root, image=photo,bg='#115982')
image_label.image = photo 
image_label.pack(pady=20)

style = ttk.Style()
style.configure("TButton", foreground="black", background="white")  # Buton stilleri

algorithms = ["Exhaustive Search", "Heuristic", "Allied Domination"]
for algorithm in algorithms:
    ttk.Button(root, text=algorithm, command=lambda a=algorithm: open_algorithm_screen(a)).pack()

root.mainloop()