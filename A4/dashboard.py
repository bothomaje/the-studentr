# Dashboard page module
from PyQt5.QtWidgets import QWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtSql import QSqlQuery
from ui_dashboard import *

# Dashboard window class
class Dashboard(QWidget):
    # Custom signals
    logout = pyqtSignal()
    planner = pyqtSignal()
    settings = pyqtSignal()
    marks = pyqtSignal()

    # Initializer function (constructor)
    def __init__(self):
        # Interface setup
        super().__init__()
        self.ui = Ui_dashboardForm()
        self.ui.setupUi(self)
        self.userID = None

        # Clock setup
        timer = QtCore.QTimer(self)
        timer.start(1000)

        #Signal/Slot connections
        self.ui.LogoutButton.clicked.connect(self.logout.emit)
        self.ui.ViewPlannerButton.clicked.connect(self.planner.emit)
        self.ui.SettingsButton.clicked.connect(self.settings.emit)
        self.ui.ViewMarksButton.clicked.connect(self.marks.emit)
        timer.timeout.connect(self.showlcd)
        
        # Display window on screen
        self.show()

    # Slots and member functions
    # Set user id for database operations
    def setUserID(self, userID):
        self.userID = userID

    # Loads all information on dashboard - default loader
    def loadDashboard(self):
        self.loadName()
        self.loadUpcomingAssignments()
        self.loadLastMark()
        self.showlcd()

    # Loads user's name on the top of the window
    def loadName(self):
        # Fetch user's first name from the database
        query = QSqlQuery()
        query.prepare("SELECT first_name from users WHERE user_id = ?")
        query.addBindValue(self.userID)
        query.exec()
        query.next()

        # Populate the welcome message and display it in label
        welcomemsg = "Hey " + query.value(0) + "!"
        self.ui.labelHello.setText(welcomemsg)

    # Loads the user's upcoming assignments on the screen
    def loadUpcomingAssignments(self):
        self.ui.listUpcoming.clear()

        # Fetch upcoming assignments from database
        query = QSqlQuery()
        query.prepare(
            """
                SELECT a.due_date, m.module_code, a.assignment_title 
                FROM assignments a 
                JOIN modules m ON a.module_id = m.module_id 
                WHERE m.user_id = ? AND a.status <> 'Done' AND a.due_date >= CURDATE() 
                ORDER BY a.due_date, a.due_time 
                LIMIT 5
            """
            )
        query.addBindValue(self.userID)
        query.exec()

        # Populate list widget with assignments
        while query.next():
            dueDate = query.value(0)
            moduleCode = query.value(1)
            title = query.value(2)
            item = dueDate.toString("dd MMM") + " - " + moduleCode + ": " + title
            self.ui.listUpcoming.addItem(QListWidgetItem(item))

    # Loads the last uploaded mark from the database
    def loadLastMark(self):
        # Fetch last assignment and mark from database
        query = QSqlQuery()
        query.prepare(
            """
                SELECT m.module_code, a.assignment_title, mk.score 
                FROM marks mk 
                JOIN assignments a ON mk.assignment_id = a.assignment_id 
                JOIN modules m ON a.module_id = m.module_id 
                WHERE m.user_id = ?
                ORDER BY mk.updated_at DESC
                LIMIT 1
            """
            )
        query.addBindValue(self.userID)
        query.exec()

        # Verifiy that the last assignment fetched has a mark entered and populate last mark information
        if query.next():
            moduleCode = query.value(0)
            title = query.value(1)
            mark = query.value(2)
            self.ui.labelLastAssignment.setText("Here's how you did on your last assignment:")
            self.ui.labelAssignmentDetails.setText("Module: %s\nAssignment: %s\nMark: %d%%" %(moduleCode, title, mark))
            if mark >= 75:
                motivation = "Cum Laude will be knocking on the door soon, well done!"
            elif 65 <= mark < 75:
                motivation = "You're doing amazing, keep it up!"
            elif 50 <= mark < 65:
                motivation = "School is tough but you're tougher! Keep pushing, you got this!"
            else:
                motivation = "Stay strong, you've still got this!"
            self.ui.labelMotivate.setText(motivation)
        else:
            self.ui.labelLastAssignment.setText("No marks have been saved yet")
            self.ui.labelAssignmentDetails.setText("Update your marks to see your progress")
            self.ui.labelMotivate.setText("")


    # Update clock display
    def showlcd(self):
        time = QtCore.QTime.currentTime()
        text = time.toString('hh:mm')
        self.ui.lcdClock.display(text)