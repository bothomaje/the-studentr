from PyQt5.QtSql import QSqlDatabase

def connect():
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('the_studentr.sqlite')
    return db.open()