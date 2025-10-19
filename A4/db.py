from PyQt6.QtSql import QSqlDatabase

_CONN_NAME = 'the_studentr_app'

"""def connect():
    db = QSqlDatabase.database(_CONN_NAME) if QSqlDatabase.contains(_CONN_NAME) else QSqlDatabase.addDatabase('QMYSQL', _CONN_NAME)
    if not db.isOpen():
        db.setHostName('localhost')
        db.setDatabaseName('the_studentr')
        db.setUserName('root')
        db.setPassword('mce')
        return db.open()
    return True

def getConnection():
    # Get the open database connection, or None if not open.
    if QSqlDatabase.contains(_CONN_NAME):
        db = QSqlDatabase.database(_CONN_NAME)
        if db.isOpen():
            return db
    return None

def disconnect():
    if QSqlDatabase.contains(_CONN_NAME):
        db = QSqlDatabase.database(_CONN_NAME)
        if db.isOpen():
            db.close()
        QSqlDatabase.removeDatabase(_CONN_NAME)
"""

def connect():
    db = QSqlDatabase.addDatabase('QSQLITE')
    # db.setHostName('localhost')
    db.setDatabaseName('the_studentr.db')
    # db.setUserName('root')
    # db.setPassword('mce')
    return db.open()

def disconnect():
    db = QSqlDatabase.database()
    if db.isOpen():
        db.close()
    QSqlDatabase.removeDatabase(QSqlDatabase.defaultConnection)