# Planner page module
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtSql import QSqlQuery
from ui_planner import *
from add_edit_assignment import AddEditAssignment
from all_assignments import AllAssignments

class Planner(QWidget):
    # Custom signals
    dashboard = pyqtSignal()

    # Initialiser function (constructor)
    def __init__(self):
        # Interface setup
        super().__init__()
        self.ui = Ui_plannerForm()
        self.ui.setupUi(self)
        self.userID = None
        self.model = QStandardItemModel()
        self.ui.listAssignments.setModel(self.model)

        # Signal/slot connections
        self.ui.DashboardButton.clicked.connect(self.dashboard.emit)
        self.ui.AddAssignmentButton.clicked.connect(self.addAssignment)
        self.ui.calendarPlanner.clicked.connect(self.loadPlanner)
        self.ui.ShowAssignmentsButton.clicked.connect(self.showAllAssignments)
        self.ui.EditAssignmentButton.clicked.connect(self.editAssignment)
        self.ui.DeleteAssignmentButton.clicked.connect(self.deleteAssignment)
        self.ui.listAssignments.selectionModel().selectionChanged.connect(self.enableDisableUpdate)
        self.model.itemChanged.connect(self.updateStatus)

        # Display window on screen
        self.show()

    # Slots and member functions
    # Function to ensure that list view selection is cleared if user clicks outside of widget
    def mousePressEvent(self, event):
        if not self.ui.listAssignments.geometry().contains(event.pos()):
            self.ui.listAssignments.clearSelection()
        super().mousePressEvent(event)

    # Set user id for database operations
    def setUserID(self, userID):
        self.userID = userID

    # Open add assignment window
    def addAssignment(self):
        self.newAssignment = AddEditAssignment(self.userID, "add", None)
    
    # Open edit assignment window with relevant assignment details loaded
    def editAssignment(self):
        index = self.ui.listAssignments.selectedIndexes()
        item = self.model.itemFromIndex(index[0])
        id = item.data(Qt.UserRole)
        self.newAssignment = AddEditAssignment(self.userID, "edit", id)

    # Load list view per day
    def loadPlanner(self):
        # Temporarily disconnect itemChanged signal to avoid triggering updateStatus during population
        try:
            self.model.itemChanged.disconnect(self.updateStatus)
        except TypeError:
            pass  # Wasn't connected yet
        self.model.clear()
        selectedDate = self.ui.calendarPlanner.selectedDate()
        self.ui.labelDate.setText(selectedDate.toString('dddd, dd MMMM yyyy'))

        # Fetch assignment information from database
        dueDate = selectedDate.toString('yyyy-MM-dd')
        query = QSqlQuery()
        query.prepare(
            """
                SELECT m.module_code, a.assignment_title, a.assignment_id, a.status
                FROM assignments a 
                JOIN modules m ON a.module_id = m.module_id 
                WHERE m.user_id = ? AND a.due_date = ?
            """
        )
        query.addBindValue(self.userID)
        query.addBindValue(dueDate)
        query.exec()

        # Populate list view model with results from database query
        while query.next():
            line = query.value(0) + ": " + query.value(1)
            id = query.value(2)
            status = query.value(3) 
            item = QStandardItem(line)
            item.setData(id, Qt.UserRole)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if status == "Done":
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.model.appendRow(item)
        
        if self.model.rowCount() == 0:
            item = QStandardItem("No assignments saved for this day")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.model.appendRow(item)
        
        # Reconnect the itemChanged signal
        self.model.itemChanged.connect(self.updateStatus)
        self.enableDisableUpdate()

    # Open all assignment window with user's assignments
    def showAllAssignments(self):
        self.allAssignments = AllAssignments(self.userID)

    # Change button state depending on list view selection
    def enableDisableUpdate(self):
        indexes = self.ui.listAssignments.selectedIndexes()
        if indexes:
            item = self.model.itemFromIndex(indexes[0])
            # Only enable if the item is selectable and not the "No assignments..." message
            if (item.flags() & Qt.ItemIsSelectable) and item.data(Qt.UserRole) is not None:
                self.ui.EditAssignmentButton.setEnabled(True)
                self.ui.DeleteAssignmentButton.setEnabled(True)
                return
        self.ui.EditAssignmentButton.setEnabled(False)
        self.ui.DeleteAssignmentButton.setEnabled(False)
    
    # Update the submission status of an assignment when toggled in the list view
    def updateStatus(self, item):
        id = item.data(Qt.UserRole)
        query = QSqlQuery()
        query.prepare(
            """
                UPDATE assignments
                SET status = ?
                WHERE assignment_id = ?
            """
        )
        status = "Done" if item.checkState() == Qt.Checked else "Not Started"
        query.addBindValue(status)
        query.addBindValue(id)
        query.exec()

    # Remove assignment from database
    def deleteAssignment(self):
        index = self.ui.listAssignments.selectedIndexes()
        item = self.model.itemFromIndex(index[0])
        id = item.data(Qt.UserRole)
        warningText = "Are you sure you want to delete " + item.text() + " from your planner?"
        warn = QMessageBox.warning(self, "Delete assignment", warningText, QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
        if warn == QMessageBox.Yes:
            query = QSqlQuery()
            query.prepare("DELETE FROM assignments WHERE assignment_id = ?")
            query.addBindValue(id)
            query.exec()
            QMessageBox.information(self, "Delete assignment", "Assignment deleted successfully.", QMessageBox.Ok)
            self.loadPlanner()
