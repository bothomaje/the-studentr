# Main window module
# Sets up the main window and manages the loading of each form on the page
# Manages central app functions
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import db
from ui_mainwindow import *
from login import Login
from dashboard import Dashboard
from planner import Planner
from profile_form import Profile
from marks import Marks

# Main Window class
class MainWindow(QMainWindow):
    # Initializer function (constructor)
    def __init__(self):
        # Interface setup
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.userID = None # stores the user id associated with the session for all data access procedures

        # Load forms onto stacked widget
        self.loginPage = Login()
        self.dashboardPage = Dashboard()
        self.plannerPage = Planner()
        self.profilePage = Profile()
        self.marksPage = Marks()
        self.ui.stackedWidget.addWidget(self.loginPage)
        self.ui.stackedWidget.addWidget(self.dashboardPage)
        self.ui.stackedWidget.addWidget(self.plannerPage)
        self.ui.stackedWidget.addWidget(self.profilePage)
        self.ui.stackedWidget.addWidget(self.marksPage)
        self.showLogin() # Open window on login page

        # Signal/slot connections
        self.loginPage.loginSuccessful.connect(self.onSuccessfulLogin)
        self.loginPage.cancelLogin.connect(self.close)
        self.dashboardPage.logout.connect(self.showLogin)
        self.dashboardPage.planner.connect(self.showPlanner)
        self.dashboardPage.settings.connect(self.showProfile)
        self.dashboardPage.marks.connect(self.showMarks)
        self.plannerPage.dashboard.connect(self.showDashboard)
        self.profilePage.dashboard.connect(self.showDashboard)
        self.marksPage.dashboard.connect(self.showDashboard)

    # Slots and member functions
    # Closes application
    def closeEvent(self, event):
        cancelMessage = QMessageBox.question(self, "Gone so soon?", "You're about to close the application. Are you sure you?", QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
        if cancelMessage == QMessageBox.Yes:
            db.disconnect()
            event.accept()
        else:
            event.ignore()

    # Switch to dashboard when log in is successful
    def onSuccessfulLogin(self, userID):
        self.userID = userID
        self.showDashboard()

    # Switch to login page
    def showLogin(self):
        self.loginPage.resetLogin()
        self.ui.stackedWidget.setCurrentWidget(self.loginPage)

    # Switch to dashboard page
    def showDashboard(self):
        self.dashboardPage.setUserID(self.userID)
        self.dashboardPage.loadDashboard()
        self.ui.stackedWidget.setCurrentWidget(self.dashboardPage)

    # Switch to planner page
    def showPlanner(self):
        self.plannerPage.setUserID(self.userID)
        self.plannerPage.loadPlanner()
        self.ui.stackedWidget.setCurrentWidget(self.plannerPage)

    # Switch to profile settings page
    def showProfile(self):
        self.profilePage.setUserID(self.userID)
        self.profilePage.resetProfileForm()
        self.ui.stackedWidget.setCurrentWidget(self.profilePage)

    # Switch to marks page
    def showMarks(self):
        self.marksPage.setUserID(self.userID)
        self.marksPage.loadMarks()
        self.ui.stackedWidget.setCurrentWidget(self.marksPage)

# Run application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    if not db.connect(): # ensure that app can connect to database
        sys.exit(1)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
    