import sys
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal
from ui_marks import *

class Marks(QWidget):
    # Custom signals
    dashboard = pyqtSignal()

    # Initializer function (constructor)
    def __init__(self):
        super().__init__()
        self.ui = Ui_marksForm()
        self.ui.setupUi(self)
        self.userID = None
        self.ui.DashboardButton.clicked.connect(self.dashboard.emit)
        self.show()

    # Slots and member functions
    # Set user id for database operations
    def setUserID(self, userID):
        self.userID = userID

    def loadMarks(self):
        pass