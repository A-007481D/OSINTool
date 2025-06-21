import os
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextBrowser, QPushButton, QTabWidget, QSplitter, QTextEdit, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt

from core.identity import TargetIdentity
from core.correlation import find_correlations
from core.graph import create_graph_from_identity
from .graph_view import GraphView

class TargetManager(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)

        # --- Target List & Management ---
        left_panel_layout = QVBoxLayout()
        self.target_list = QListWidget()
        self.target_list.itemClicked.connect(self.display_target_data)
        self.refresh_button = QPushButton("Refresh Targets")
        self.refresh_button.clicked.connect(self.populate_target_list)
        left_panel_layout.addWidget(self.refresh_button)
        left_panel_layout.addWidget(self.target_list)

        # --- Multi-Target Input ---
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Enter usernames/emails (comma or newline separated)")
        left_panel_layout.addWidget(self.input_box)

        # --- Management Buttons ---
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Target")
        self.save_btn.clicked.connect(self.save_target)
        self.load_btn = QPushButton("Load Target")
        self.load_btn.clicked.connect(self.load_target)
        self.delete_btn = QPushButton("Delete Target")
        self.delete_btn.clicked.connect(self.delete_target)
        self.send_btn = QPushButton("Send to Scan")
        # Placeholder: connect to signal for future integration
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.send_btn)
        left_panel_layout.addLayout(btn_layout)

        # --- Data Display Tabs ---
        self.tabs = QTabWidget()
        self.raw_data_view = QTextBrowser()
        self.correlations_view = QTextBrowser()
        self.graph_view = GraphView()

        self.tabs.addTab(self.raw_data_view, "Raw Data")
        self.tabs.addTab(self.correlations_view, "Correlations")
        self.tabs.addTab(self.graph_view, "Graph")

        self.layout.addLayout(left_panel_layout, 1)
        self.layout.addWidget(self.tabs, 3)

        self.populate_target_list()

    def populate_target_list(self):
        self.target_list.clear()
        data_dir = "data"
        if not os.path.exists(data_dir):
            return
        # Show .json files as saved targets
        targets = [f[:-5] for f in os.listdir(data_dir) if f.endswith('.json')]
        self.target_list.addItems(targets)

    def display_target_data(self, item):
        target_name = item.text()
        
        # Display input box content for selected target
        data_dir = "data"
        path = os.path.join(data_dir, f"{target_name}.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.input_box.setPlainText("\n".join(data))
                except Exception:
                    self.input_box.setPlainText("")
        # --- Display Raw Data ---
        self.display_raw_data(target_name)
        # --- Display Correlations ---
        self.display_correlations(target_name)

    def save_target(self):
        # Prompt for target profile name
        name, ok = QInputDialog.getText(self, "Save Target", "Enter a name for this target profile:")
        if not ok or not name.strip():
            return
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        # Parse input (split by comma/newline, strip, dedup)
        entries = self.input_box.toPlainText().replace(",", "\n").split("\n")
        entries = sorted(set([x.strip() for x in entries if x.strip()]))
        if not entries:
            QMessageBox.warning(self, "No Data", "No usernames or emails entered.")
            return
        path = os.path.join(data_dir, f"{name}.json")
        with open(path, 'w') as f:
            json.dump(entries, f, indent=2)
        self.populate_target_list()

    def load_target(self):
        item = self.target_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection", "Select a target to load.")
            return
        self.display_target_data(item)

    def delete_target(self):
        item = self.target_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection", "Select a target to delete.")
            return
        name = item.text()
        data_dir = "data"
        path = os.path.join(data_dir, f"{name}.json")
        if os.path.exists(path):
            os.remove(path)
        self.populate_target_list()
        self.input_box.clear()

    def display_raw_data(self, target_name):
        target_dir = os.path.join("data", target_name)
        self.raw_data_view.clear()
        html = f"<h1>{target_name}</h1>"

        if not os.path.isdir(target_dir):
            self.raw_data_view.setHtml(html)
            return

        for filename in sorted(os.listdir(target_dir)):
            if filename.endswith(".json"):
                file_path = os.path.join(target_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                scan_type = filename.replace(".json", "").replace("_", " ").title()
                html += f"<h2>{scan_type}</h2>"

                if scan_type == "Username":
                    if data:
                        html += "<ul>"
                        for url in data:
                            html += f"<li><a href='{url}'>{url}</a></li>"
                        html += "</ul>"
                    else:
                        html += "<p>No accounts found.</p>"
                else:
                    html += self.format_dict_to_html_table(data)
        
        self.raw_data_view.setHtml(html)

    def display_correlations(self, target_name):
        identity = TargetIdentity(target_name)
        correlations = find_correlations(identity)

        # Update Correlations Tab
        self.correlations_view.clear()
        corr_html = f"<h1>Correlations for {target_name}</h1>"
        if not any(correlations.values()):
            corr_html += "<p>No correlations found.</p>"
        else:
            corr_html += self.format_correlations_to_html(correlations)
        self.correlations_view.setHtml(corr_html)

        # Update Graph View
        graph = create_graph_from_identity(identity, correlations)
        self.graph_view.update_graph(graph)

    def format_correlations_to_html(self, correlations):
        html = ""
        for key, values in correlations.items():
            if not values:
                continue

            html += f"<h3>{key.replace('_', ' ').title()}</h3>"

            if isinstance(values, list):
                html += "<ul>"
                for value in values:
                    html += f"<li>{value}</li>"
                html += "</ul>"
            elif isinstance(values, dict):
                # Re-use the existing table formatting for dictionaries
                html += self.format_dict_to_html_table(values)
            else:
                html += f"<p>{values}</p>"
        return html

    def format_dict_to_html_table(self, data):
        if not data:
            return "<p>No data found.</p>"
        
        table_html = "<style> table { width: 100%; border-collapse: collapse; font-family: sans-serif; } th, td { padding: 8px; text-align: left; border-bottom: 1px solid #444; } th { background-color: #222; color: #eee; } tr:nth-child(even) {background-color: #333;} </style>"
        table_html += "<table>"
        for key, value in data.items():
            key_str = str(key).replace('_', ' ').title()
            if isinstance(value, list):
                value_str = "<br>".join(map(str, value))
            else:
                value_str = str(value)
            table_html += f"<tr><td style='width: 25%;'><b>{key_str}</b></td><td>{value_str}</td></tr>"
        table_html += "</table>"
        return table_html
