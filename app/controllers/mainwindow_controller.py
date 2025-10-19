from app.views.mainwindow_view import MainWindowView

class MainWindowController:
    def __init__(self, view: MainWindowView):
        self.view = view

        # self.loginPage = Login()
        # self.dashboardPage = Dashboard()
        # self.plannerPage = Planner()
        # self.profilePage = Profile()
        # self.marksPage = Marks()

        # self.ui.stackedWidget.addWidget(self.loginPage)
        # self.ui.stackedWidget.addWidget(self.dashboardPage)
        # self.ui.stackedWidget.addWidget(self.plannerPage)
        # self.ui.stackedWidget.addWidget(self.profilePage)
        # self.ui.stackedWidget.addWidget(self.marksPage)
        # self.showLogin() # Open window on login page

        '''
        self.loginPage.loginSuccessful.connect(self.onSuccessfulLogin)
        self.loginPage.cancelLogin.connect(self.close)
        self.dashboardPage.logout.connect(self.showLogin)
        self.dashboardPage.planner.connect(self.showPlanner)
        self.dashboardPage.settings.connect(self.showProfile)
        self.dashboardPage.marks.connect(self.showMarks)
        self.plannerPage.dashboard.connect(self.showDashboard)
        self.profilePage.dashboard.connect(self.showDashboard)
        self.marksPage.dashboard.connect(self.showDashboard)

        self._show_login()

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
        '''

        