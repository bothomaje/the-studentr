# Login page module
from PyQt5.QtWidgets import QWidget, QLineEdit
from PyQt5.QtCore import pyqtSignal
from .gen.login_ui import *

# Login window class
class LoginForm(QWidget):
    # Custom Signals
    cancel_login = pyqtSignal()

    # Initialiser function (constructor)
    def __init__(self, user_model):
        # Interface setup
        super().__init__()
        self.ui = Ui_loginForm()
        self.ui.setupUi(self)

        # Set model
        self.model = user_model
        
        # Slot/signal connections
        self.ui.checkShowPass.stateChanged.connect(self.show_hide_password)
        self.ui.LoginButton.clicked.connect(self._login)
        self.ui.CancelButton.clicked.connect(self.cancel_login.emit)
        self.model.user_not_found.connect(self._display_user_not_found)
        self.model.incorrect_password.connect(self._display_bad_pwd)
        self.model.successful_login.connect(self.reset_login)
    
    # Set window to default state
    def reset_login(self):
        self.ui.lineUsername.clear()
        self.ui.linePassword.clear()
        self.ui.lineUsername.setFocus()
        self.ui.checkShowPass.setChecked(False)
        self.ui.labelMismatch.setText("")

    # Show or hide password
    def show_hide_password(self):
        if self.ui.checkShowPass.isChecked():
            self.ui.linePassword.setEchoMode(QLineEdit.Normal)
        else:
            self.ui.linePassword.setEchoMode(QLineEdit.Password)
    
    def _display_user_not_found(self):
        self.ui.labelMismatch.setText("User not found. Please try again.")

    def _display_bad_pwd(self):
        self.ui.labelMismatch.setText("Incorrect password. Please try again.")

    # Verify username and password
    def _login(self):
        username = self.ui.lineUsername.text()
        password = self.ui.linePassword.text()
        self.model.authenticate_user(username, password)
