import sys
from PyQt5.QtWidgets import QApplication, QDialog
import qdarkstyle

from ui.dashboard import Dashboard
from ui.lock_screen import LockScreen

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    
    lock = LockScreen()
    if lock.exec_() == QDialog.Accepted:
        window = Dashboard()
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
