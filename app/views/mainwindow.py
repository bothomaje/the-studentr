from PyQt5.QtWidgets import QMainWindow, QStackedLayout, QWidget
from PyQt5.QtGui import QIcon
from .gen import resources_rc

class MainWindowView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 400)
        self.setWindowTitle("theStudentr")
        self.setWindowIcon(QIcon(":/img/logo.svg"))

        mainLayout = QStackedLayout()
        
        mainLayout.setCurrentIndex(0)
        
        central = QWidget()
        central.setLayout(mainLayout)
        self.setCentralWidget(central)
    