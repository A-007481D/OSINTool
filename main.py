import sys
from PyQt5.QtWidgets import QApplication
import qdarkstyle

from ui.dashboard import Dashboard

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    
    window = Dashboard()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
