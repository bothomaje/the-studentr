from PyQt5.QtWidgets import QMainWindow, QStackedLayout, QWidget
from PyQt5.QtGui import QIcon
from .gen import resources_rc
from .login import LoginForm
from models import user_model

class MainWindowView(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self._db = db
        self.user_model = user_model.UserModel(self._db)

        self.resize(800, 400)
        self.setWindowTitle("theStudentr")
        self.setWindowIcon(QIcon(":/img/logo.svg"))


        mainLayout = QStackedLayout()
        mainLayout.addWidget(LoginForm(self.user_model))
        mainLayout.setCurrentIndex(0)
        
        central = QWidget()
        central.setLayout(mainLayout)
        self.setCentralWidget(central)

        self.user_model.successful_login.connect(self.show_dashboard)
    
    def show_dashboard(self):
        print("Showing dashboard...")