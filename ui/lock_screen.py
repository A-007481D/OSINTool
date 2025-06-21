import sys
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt
import json
import os
import hashlib

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config/settings.json'))

class LockScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('OSINT Intelligence Terminal - Unlock')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.setFixedSize(350, 180)
        self.setup_ui()
        self.load_or_init_password()

    def setup_ui(self):
        self.label = QLabel('Enter Password:', self)
        self.input = QLineEdit(self)
        self.input.setEchoMode(QLineEdit.Password)
        self.button = QPushButton('Unlock', self)
        self.button.clicked.connect(self.check_password)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def load_or_init_password(self):
        if not os.path.exists(CONFIG_PATH):
            self.set_password()
        else:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            self.stored_hash = config.get('password_hash')
            if not self.stored_hash:
                self.set_password()

    def set_password(self):
        pw, ok = QInputDialog.getText(self, 'Set Password', 'Set a new password:', QLineEdit.Password)
        if ok and pw:
            hash_ = hashlib.sha256(pw.encode()).hexdigest()
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump({'password_hash': hash_}, f)
            self.stored_hash = hash_
            QMessageBox.information(self, 'Password Set', 'Password saved. Please enter it to unlock.')
        else:
            QMessageBox.warning(self, 'No Password', 'Password not set. Exiting.')
            sys.exit(0)

    def check_password(self):
        pw = self.input.text()
        if hashlib.sha256(pw.encode()).hexdigest() == self.stored_hash:
            self.accept()
        else:
            QMessageBox.warning(self, 'Incorrect', 'Incorrect password.')
            self.input.clear()
