from PyQt6.QtWidgets import QMainWindow, QMessageBox
from gen.ui_mainwindow import *

class MainWindowView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

    
    