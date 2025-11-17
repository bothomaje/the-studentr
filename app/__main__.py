import sys
from PyQt5.QtWidgets import QApplication
from db import db
from views.mainwindow import MainWindowView

def main():
    app = QApplication(sys.argv)
    if not db.connect():
        sys.exit(1)
    window = MainWindowView()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
    