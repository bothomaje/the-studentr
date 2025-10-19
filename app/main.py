import sys
from PyQt6.QtWidgets import QApplication
from views.mainwindow_view import MainWindowView

def main():
    app = QApplication(sys.argv)
    main = MainWindowView()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()