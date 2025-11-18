from PyQt5.QtSql import QSqlQueryModel, QSqlQuery
from PyQt5.QtCore import pyqtSignal

class UserModel(QSqlQueryModel):
    user_not_found = pyqtSignal()
    incorrect_password = pyqtSignal()
    successful_login = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.model = QSqlQueryModel()
    
    def authenticate_user(self, username, password):
        query = QSqlQuery()
        query.prepare("SELECT * FROM users WHERE username = :username")
        query.bindValue(":username", username)
        if not query.exec():
            self.user_not_found.emit()
            return
        
        if not query.first():
            self.user_not_found.emit()
            return
        
        pwd = query.value("password")
        if password != pwd:
            self.incorrect_password.emit()
        else:
            self.model.setQuery(query)
            self.successful_login.emit()
