# Login page module
from PyQt5.QtWidgets import QWidget, QLineEdit
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtSql import QSqlQuery
from ui_login import *

# Login window class
class Login(QWidget):
    # Custom Signals
    loginSuccessful = pyqtSignal(str)
    cancelLogin = pyqtSignal()

    # Initialiser function (constructor)
    def __init__(self):
        # Interface setup
        super().__init__()
        self.ui = Ui_loginForm()
        self.ui.setupUi(self)
        
        # Slot/signal connections
        self.ui.checkShowPass.stateChanged.connect(self.showHidePassword)
        self.ui.LoginButton.clicked.connect(self.validateLogin)
        self.ui.CancelButton.clicked.connect(self.cancelLogin.emit)
        
        # Display window on screen
        self.show()
    
    # Set window to default state
    def resetLogin(self):
        self.ui.lineUsername.clear()
        self.ui.linePassword.clear()
        self.ui.checkShowPass.setChecked(False)
        self.ui.labelMismatch.setText("")

    # Show or hide password
    def showHidePassword(self):
        if self.ui.checkShowPass.isChecked():
            self.ui.linePassword.setEchoMode(QLineEdit.Normal)
        else:
            self.ui.linePassword.setEchoMode(QLineEdit.Password)
    
    # Verify username and password
    def validateLogin(self):
        username = self.ui.lineUsername.text()
        password = self.ui.linePassword.text()
        
        # hard coded username and password verification
        if username != "Maje" or password != "24744913":
            self.ui.labelMismatch.setText("Incorrect username/password - please try again")
        else:
            # Fetch associated user id from database and sent it to main window
            query = QSqlQuery()
            query.prepare("SELECT user_id FROM users WHERE username = ?")
            query.addBindValue(username)
            query.exec()
            if query.next():
                userID = query.value(0)
            else:
                userID = ""
            self.loginSuccessful.emit(userID)
