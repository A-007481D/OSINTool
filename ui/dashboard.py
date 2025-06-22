import json
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextBrowser, QComboBox, QTabWidget, QProgressBar, QLabel, QScrollArea, QFrame
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt

from collectors.sherlock import scan_username, RealtimeNotifier
from collectors.whois import get_whois_info
from collectors.ipinfo import get_ip_info
from ui.target_manager import TargetManager
from core.json_utils import safe_json_dump

class Worker(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, int)
    partial_result = pyqtSignal(str, str, str)

    def __init__(self, scan_type, target):
        super().__init__()
        self.scan_type = scan_type
        self.target = target

    def run(self):
        try:
            if self.scan_type == "Username":
                notifier = RealtimeNotifier()
                notifier.progress.connect(self.progress)
                notifier.result_found.connect(self.partial_result)
                # scan_username is now non-blocking in terms of final result,
                # but the work is done in-thread and progress is emitted.
                scan_username(self.target, notifier=notifier)
                # Emit an empty list to signal completion of this scan type.
                self.result.emit([])
            elif self.scan_type == "Domain":
                data = get_whois_info(self.target)
                self.result.emit(data)
            elif self.scan_type == "IP Address":
                data = get_ip_info(self.target)
                self.result.emit(data)
            else:
                self.result.emit(None)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSINT Desktop Intelligence Tool")
        self.setGeometry(100, 100, 1200, 800)
        self.current_results = []

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.live_scan_widget = QWidget()
        self.tabs.addTab(self.live_scan_widget, "Live Scan")
        self.setup_live_scan_ui()

        self.target_manager_widget = TargetManager()
        self.tabs.addTab(self.target_manager_widget, "Targets")

        self.statusBar().showMessage("Ready")

    def setup_live_scan_ui(self):
        live_scan_layout = QVBoxLayout(self.live_scan_widget)

        # --- Input Area ---
        input_layout = QHBoxLayout()
        self.target_input = QLineEdit()
        self.scan_type_combo = QComboBox()
        self.scan_type_combo.addItems(["Username", "Real Name", "Domain", "IP Address"])
        self.scan_button = QPushButton("Scan")
        self.save_button = QPushButton("Save Results")

        input_layout.addWidget(self.target_input)
        input_layout.addWidget(self.scan_type_combo)
        input_layout.addWidget(self.scan_button)
        input_layout.addWidget(self.save_button)
        live_scan_layout.addLayout(input_layout)

        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        live_scan_layout.addWidget(self.progress_bar)

        # --- Profile Card Scroll Area ---
        self.card_scroll = QScrollArea()
        self.card_scroll.setWidgetResizable(True)
        self.card_container = QWidget()
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_layout.setAlignment(Qt.AlignTop)
        self.card_scroll.setWidget(self.card_container)
        live_scan_layout.addWidget(self.card_scroll)

        # --- Connections and Initial State ---
        self.scan_button.clicked.connect(self.start_scan)
        self.save_button.clicked.connect(self.save_results)
        self.save_button.setEnabled(False)
        self.scan_type_combo.currentIndexChanged.connect(self.update_input_placeholder)
        self.update_input_placeholder() # Set initial placeholder

    def update_input_placeholder(self):
        scan_type = self.scan_type_combo.currentText()
        if scan_type == "Username":
            self.target_input.setPlaceholderText("Enter username")
        elif scan_type == "Real Name":
            self.target_input.setPlaceholderText("Enter full name")
        elif scan_type == "Domain":
            self.target_input.setPlaceholderText("Enter domain (e.g. example.com)")
        elif scan_type == "IP Address":
            self.target_input.setPlaceholderText("Enter IP address")

    def start_scan(self):
        self.target = self.target_input.text()
        self.current_scan_type = self.scan_type_combo.currentText()

        if not self.target:
            self.statusBar().showMessage("Error: Target cannot be empty.")
            return

        self.scan_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.current_results = []
        self.statusBar().showMessage(f"Scanning {self.current_scan_type} for '{self.target}'...")
        # Clear profile cards
        for i in reversed(range(self.card_layout.count())):
            widget = self.card_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if self.current_scan_type == "Username":
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

        self.thread = QThread()
        self.worker = Worker(self.current_scan_type, self.target)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.result.connect(self.display_results)
        self.worker.error.connect(self.scan_error)
        self.worker.progress.connect(self.update_progress)
        self.worker.partial_result.connect(self.append_username_result)

        self.thread.start()

    def update_progress(self, value, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(value)

    def append_username_result(self, site, url, status):
        # Enrich profile (async could be added later for speed)
        enriched = self.enrich_profile(url, site)
        self.current_results.append(enriched)
        self.update_results_table()

    def update_results_table(self):
        # Clear previous cards
        for i in reversed(range(self.card_layout.count())):
            widget = self.card_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        if not self.current_results:
            label = QLabel("No profiles found.")
            label.setStyleSheet("color: #ccc; font-size: 16px;")
            self.card_layout.addWidget(label)
            return
        for entry in self.current_results:
            card = ProfileCard(entry)
            self.card_layout.addWidget(card)

    def enrich_profile(self, url, site):
        try:
            from core.profile_enrich import enrich_profile as real_enrich
            info = real_enrich(url, site)
        except Exception:
            info = {}
        entry = {
            "site": site,
            "url": url,
            "bio": info.get("bio", ""),
            "avatar_url": info.get("avatar_url", ""),
            "followers": info.get("followers", ""),
            "following": info.get("following", "")
        }
        return entry

    def save_results(self):
        if not self.current_results:
            self.statusBar().showMessage("No results to save.", 5000)
            return

        data_dir = "data"
        target_dir = os.path.join(data_dir, self.target)
        os.makedirs(target_dir, exist_ok=True)

        file_name = f"{self.current_scan_type.replace(' ', '_').lower()}.json"
        file_path = os.path.join(target_dir, file_name)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                safe_json_dump(self.current_results, f, indent=4)
            self.statusBar().showMessage(f"Results saved to {file_path}", 5000)
            self.target_manager_widget.populate_target_list()
        except Exception as e:
            self.statusBar().showMessage(f"Error saving results: {e}", 5000)

    def format_dict_to_html_table(self, data):
        if not data:
            return "<p>No data found.</p>"
        
        html = "<style> table { width: 100%; border-collapse: collapse; font-family: sans-serif; } th, td { padding: 8px; text-align: left; border-bottom: 1px solid #444; } th { background-color: #222; color: #eee; } tr:nth-child(even) {background-color: #333;} </style>"
        html += "<table>"
        for key, value in data.items():
            key_str = str(key).replace('_', ' ').title()
            if isinstance(value, list):
                value_str = "<br>".join(map(str, value))
            else:
                value_str = str(value)
            html += f"<tr><td style='width: 25%;'><b>{key_str}</b></td><td>{value_str}</td></tr>"
        html += "</table>"
        return html

    def display_results(self, data):
        # Clear previous cards
        for i in reversed(range(self.card_layout.count())):
            widget = self.card_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        if self.current_scan_type == "Real Name":
            # Real person OSINT search
            try:
                from core.people_search import search_person
                people = search_person(self.target)
                if not people:
                    card = QLabel("<span style='color:#ffb347;font-size:18px;'>No public profiles found for this name.</span>")
                    self.card_layout.addWidget(card)
                else:
                    for entry in people:
                        self.card_layout.addWidget(ProfileCard({
                            "name": entry.get("name", ""),
                            "site": entry.get("site", ""),
                            "bio": entry.get("title", ""),
                            "avatar_url": entry.get("avatar_url", ""),
                            "location": entry.get("location", ""),
                            "emails": entry.get("emails", []),
                            "phones": entry.get("phones", []),
                            "url": entry.get("profile_url", ""),
                            "snippet": entry.get("snippet", "")
                        }))
                self.progress_bar.setVisible(False)
            except Exception as e:
                card = QLabel(f"<span style='color:red;'>Error searching for people: {e}</span>")
                self.card_layout.addWidget(card)
                self.progress_bar.setVisible(False)
        elif self.current_scan_type != "Username":
            # Show non-username results as a card
            self.current_results = data
            html = self.format_dict_to_html_table(data)
            card = QLabel(html)
            card.setStyleSheet("color: #eee; font-size: 15px;")
            card.setTextFormat(Qt.RichText)
            self.card_layout.addWidget(card)
            self.progress_bar.setVisible(False)
        else:
            self.progress_bar.setVisible(False)
            self.update_results_table()

        self.statusBar().showMessage("Scan finished.", 5000)
        self.scan_button.setEnabled(True)
        if self.current_results:
            self.save_button.setEnabled(True)

    def scan_error(self, error_message):
        self.progress_bar.setVisible(False)
        # Show error in card area
        error_label = QLabel(f"<p style='color: red;'>An error occurred:<br>{error_message}</p>")
        self.card_layout.addWidget(error_label)
        self.statusBar().showMessage("Scan failed.", 5000)
        self.scan_button.setEnabled(True)
