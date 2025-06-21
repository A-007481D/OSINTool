import os
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextBrowser, QPushButton, QTabWidget

from core.identity import TargetIdentity
from core.correlation import find_correlations

class TargetManager(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)

        # --- Target List ---
        left_panel_layout = QVBoxLayout()
        self.target_list = QListWidget()
        self.target_list.itemClicked.connect(self.display_target_data)
        self.refresh_button = QPushButton("Refresh Targets")
        self.refresh_button.clicked.connect(self.populate_target_list)
        left_panel_layout.addWidget(self.refresh_button)
        left_panel_layout.addWidget(self.target_list)

        # --- Data Display Tabs ---
        self.data_tabs = QTabWidget()
        self.raw_data_display = QTextBrowser()
        self.correlation_display = QTextBrowser()
        self.data_tabs.addTab(self.raw_data_display, "Raw Data")
        self.data_tabs.addTab(self.correlation_display, "Correlations")

        self.layout.addLayout(left_panel_layout, 1)
        self.layout.addWidget(self.data_tabs, 3)

        self.populate_target_list()

    def populate_target_list(self):
        self.target_list.clear()
        data_dir = "data"
        if not os.path.exists(data_dir):
            return
        
        targets = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
        self.target_list.addItems(targets)

    def display_target_data(self, item):
        target_name = item.text()
        
        # --- Display Raw Data ---
        self.display_raw_data(target_name)

        # --- Display Correlations ---
        self.display_correlations(target_name)

    def display_raw_data(self, target_name):
        target_dir = os.path.join("data", target_name)
        self.raw_data_display.clear()
        html = f"<h1>{target_name}</h1>"

        if not os.path.isdir(target_dir):
            self.raw_data_display.setHtml(html)
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
        
        self.raw_data_display.setHtml(html)

    def display_correlations(self, target_name):
        identity = TargetIdentity(target_name)
        correlations = find_correlations(identity)
        self.correlation_display.clear()
        
        corr_html = f"<h1>Correlations for {target_name}</h1>"
        if not any(correlations.values()):
             corr_html += "<p>No correlations found.</p>"
        else:
            corr_html += self.format_correlations_to_html(correlations)

        self.correlation_display.setHtml(corr_html)

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
