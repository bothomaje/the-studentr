import sys
from PyQt5.QtWidgets import QApplication
from db import db
from views.mainwindow import MainWindow

def main():
    app = QApplication(sys.argv)
    if not db.connect():
        sys.exit(1)
    window = MainWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
    