# All Assignments Module
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from PyQt5.QtCore import QDate
from PyQt5.QtSql import QSqlQuery
from ui_all_assignments import *

class AllAssignments(QDialog):
    # Initialiser function (constructor)
    def __init__(self, userID):
        # Interface setup
        super().__init__()
        self.ui = Ui_showAllDialog()
        self.ui.setupUi(self)
        self.userID = userID
        self.loadAssignments()

        # Signal/slot connections
        self.ui.OkButton.clicked.connect(self.close)

        self.show()

    # Slots and member functions
    # 
    def loadAssignments(self):
        # Fetch assignments from DB
        query = QSqlQuery()
        query.prepare(
            """
                SELECT m.module_code, a.assignment_title, a.due_date, a.due_time, a.status 
                FROM assignments a 
                JOIN modules m ON a.module_id = m.module_id 
                WHERE m.user_id = ?
                ORDER BY a.due_date, a.due_time
            """
            )
        query.addBindValue(self.userID)
        query.exec()

        # Populate table widget
        while query.next():
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.setRowCount(row + 1)
            moduleCode = query.value(0)
            title = query.value(1)
            date = query.value(2)
            time = query.value(3)
            status = query.value(4)
            due = date.toString("d MMMM yyyy") + " " + time

            # Calculate number of days left
            days_left = QDate.currentDate().daysTo(date)
            days_left = 0 if days_left < 0 else days_left
            
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(moduleCode))
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(title))
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(due))
            self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(str(days_left)))
            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(status))

        # Table Widget layout
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.resizeRowsToContents()
    