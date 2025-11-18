import sys
from PyQt5.QtWidgets import QApplication
from db import db
from views.mainwindow import MainWindowView

def main(db):
    app = QApplication(sys.argv)
    if not db:
        sys.exit(1)
    window = MainWindowView(db)
    window.show()
    return app.exec_()

if __name__ == "__main__":
    conn = db.connect()
    sys.exit(main(conn))
    