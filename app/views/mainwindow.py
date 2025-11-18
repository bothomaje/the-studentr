from PyQt5.QtWidgets import QMainWindow, QStackedLayout, QWidget, QMessageBox
from PyQt5.QtGui import QIcon
from .gen import resources_rc
from .login import LoginForm
from models import user_model

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_model = user_model.UserModel()
        self.login = LoginForm(self.user_model)

        self.resize(800, 400)
        self.setWindowTitle("theStudentr")
        self.setWindowIcon(QIcon(":/img/logo.svg"))

        mainLayout = QStackedLayout()
        mainLayout.addWidget(self.login)
        mainLayout.setCurrentIndex(0)
        
        central = QWidget()
        central.setLayout(mainLayout)
        self.setCentralWidget(central)

        self.login.cancel_login.connect(self.close)
        self.user_model.successful_login.connect(self.show_dashboard)
    
    def closeEvent(self, event):
        cancelMessage = QMessageBox.question(self, "Gone so soon?", "You're about to close the application. Are you sure you?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if cancelMessage == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def show_dashboard(self):
        print("Showing dashboard...")