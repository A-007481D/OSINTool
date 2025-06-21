from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx
import matplotlib.pyplot as plt

class GraphView(QWidget):
    """A widget to display a NetworkX graph using Matplotlib."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_graph(self, G):
        """Clears the current figure and draws the new graph G."""
        self.figure.clear()
        if not G or G.number_of_nodes() == 0:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "No data to visualize.", ha='center', va='center')
            self.canvas.draw()
            return

        ax = self.figure.add_subplot(111)
        pos = nx.spring_layout(G, k=0.5, iterations=50)  # Position nodes

        # Define colors for different node types
        node_colors = []
        for node in G.nodes():
            node_type = G.nodes[node].get('type')
            if node_type == 'target':
                node_colors.append('#ff4757')  # Red
            elif node_type == 'email':
                node_colors.append('#2ed573')  # Green
            elif node_type == 'registrar':
                node_colors.append('#1e90ff')  # Blue
            elif node_type == 'name_server':
                node_colors.append('#ffa502')  # Orange
            elif node_type == 'registrant':
                node_colors.append('#706fd3')  # Purple
            else:
                node_colors.append('#7f8fa6')  # Grey

        nx.draw(G, pos, ax=ax, with_labels=True, node_color=node_colors,
                node_size=2000, font_size=8, font_color='white',
                edge_color='gray')

        ax.set_title("Target Correlations")
        self.canvas.draw()
