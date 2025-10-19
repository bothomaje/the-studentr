# Add/Edit Assignments Window Module
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import QDate, QDateTime, QTime
from PyQt6.QtSql import QSqlQuery
from ui_add_edit_assignment import *

class AddEditAssignment(QDialog):
    # Initialiser function (constructor)
    def __init__(self, userID, mode, assignmentID):
        super().__init__()
        self.ui = Ui_addEditAssignmentDialog()
        self.ui.setupUi(self)
        self.userID = userID
        self.mode = mode
        self.assignmentID = assignmentID
        self.moduleID = None
        self.initUi()

        self.ui.CancelButton.clicked.connect(self.close)
        self.ui.AddAssignmentButton.clicked.connect(self.addAssignment)

        
    # Slots and member functions
    # 
    def initUi(self):
        if self.mode == "add":
            self.setWindowTitle("Add New Assignment")
            self.ui.labelHeading.setText("Enter your new assignment details below:")
            self.ui.comboModuleName.clear()
            
            query = QSqlQuery()
            query.prepare("SELECT DISTINCT module_name FROM modules WHERE user_id = ?")
            query.addBindValue(self.userID)
            if query.exec():
                while query.next():
                    module_name = query.value(0)
                    self.ui.comboModuleName.addItem(module_name)
            self.ui.comboModuleName.setEnabled(True)

            # Set date/time edits to current date and time
            current_date = QDate.currentDate()
            current_time = QDateTime.currentDateTime().time()
            self.ui.dateTimeOpen.setDate(current_date)
            self.ui.dateTimeOpen.setTime(current_time)
            self.ui.dateTimeDue.setDate(current_date)
            self.ui.dateTimeDue.setTime(current_time)
            self.show()
        elif self.mode == "edit":
            self.setWindowTitle("Edit Assignment Details")
            self.ui.labelHeading.setText("Update your assignment details below:")
            self.ui.comboModuleName.clear()
            query = QSqlQuery()

            query.prepare(
                """
                    SELECT a.module_id, m.module_name, a.assignment_title, a.category, a.assignment_type, a.start_date, a.due_date, a.due_time
                    FROM assignments a
                    JOIN modules m ON a.module_id = m.module_id
                    WHERE a.assignment_id = ? 
                """
                )
            query.addBindValue(self.assignmentID)
            query.exec()
            query.next()
            self.moduleID = query.value(0)
            moduleName = query.value(1)
            title = query.value(2)
            category = query.value(3)
            type = query.value(4)
            start = query.value(5)
            dueDate = query.value(6)
            dueTime = query.value(7)
            qdue = QTime.fromString(dueTime, "HH:mm")
            self.ui.comboModuleName.addItem(moduleName)
            self.ui.comboModuleName.setEnabled(False)
            self.ui.lineAssignmentName.setText(title)
            if category == "Formative":
                self.ui.radioFormative.setChecked(True)
            else:
                self.ui.radioExam.setChecked(True)
            self.ui.comboType.setCurrentIndex(self.ui.comboType.findText(type))
            self.ui.dateTimeOpen.setDate(start)
            self.ui.dateTimeDue.setDate(dueDate)
            self.ui.dateTimeDue.setTime(qdue)
            self.show()
        else:
            print("Incorrect mode selected")
            self.close()
        
        

    def addAssignment(self):
        moduleName = self.ui.comboModuleName.currentText()
        assignmentName = self.ui.lineAssignmentName.getText()
        if self.ui.radioFormative.isChecked():
            category = "Formative"
        else:
            category = "Exam"
        assignmentType = self.ui.comboType.currentText()
        startDate = self.ui.dateTimeOpen.date()
        dueDate = self.ui.dateTimeDue.date()
        dueTime = self.ui.dateTimeDue.time()
        query = QSqlQuery()