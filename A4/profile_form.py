# Profile page module
import os
import shutil
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath
from ui_profile import *

# Profile Window class
class Profile(QWidget):
    # Custom signals
    dashboard = pyqtSignal()

    # Initializer function (constructor)
    def __init__(self):
        # Interface setup
        super().__init__()
        self.ui = Ui_profileForm()
        self.ui.setupUi(self)
        self.userID = None

        # Signal/slot connections
        self.ui.DashboardButton.clicked.connect(self.dashboard.emit)
        self.ui.EditDetailsButton.clicked.connect(self.enableEdit)
        self.ui.SaveButton.clicked.connect(self.saveChanges)
        self.ui.CancelButton.clicked.connect(self.resetProfileForm)
        self.ui.EditPhotoButton.clicked.connect(self.editProfilePhoto)
        self.ui.ClearPhotoButton.clicked.connect(self.clearProfilePhoto)

        # Display window on screen
        self.show()

    # Slots and member functions
    # Set user id for database operations
    def setUserID(self, userID):
        self.userID = userID

    # Load profile photo on page
    def loadProfilePhoto(self):
        # Check folder for saved profile photo
        height = self.ui.labelProfilePhoto.height()
        width = self.ui.labelProfilePhoto.width()
        picturesDir = os.path.join(os.path.dirname(__file__), "resources/assets/images/usrs")
        for ext in (".jpg", ".png", ".jpeg"):
            pictureName = self.userID + ext
            userPhoto = os.path.join(picturesDir, pictureName)
            # If the user has set a profile photo, display it in a rounded icon
            if os.path.exists(userPhoto):
                pixmap = QPixmap(userPhoto).scaled(height, width, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.ui.ClearPhotoButton.setEnabled(True)
                rounded = QPixmap(height, width)
                rounded.fill(Qt.transparent)
                painter = QPainter(rounded)
                painter.setRenderHint(QPainter.Antialiasing)
                path = QPainterPath()
                path.addEllipse(0, 0, height, width)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, pixmap)
                painter.end()
                self.ui.labelProfilePhoto.setPixmap(rounded)
                break
        else: # If there is no profile photo, then a default icon is loaded
            pixmap = QPixmap(":/icons/user.png")
            self.ui.labelProfilePhoto.setPixmap(pixmap)
            self.ui.ClearPhotoButton.setEnabled(False)
        
    # Load profile page with user information
    def loadProfile(self):
        # Load profile photo on window
        self.loadProfilePhoto()

        # Fetch user information from database
        query = QSqlQuery()
        query.prepare("SELECT username, first_name, surname, email, dob FROM users WHERE user_id = ?")
        query.addBindValue(self.userID)
        query.exec()

        # Populate user information on window
        if query.next():
            self.ui.lineUsername.setText(query.value(0))
            self.ui.lineFirstName.setText(query.value(1))
            self.ui.lineSurname.setText(query.value(2))
            self.ui.lineEmail.setText(query.value(3))
            birthday = query.value(4)
            if birthday is not None:
                self.ui.dateBirthday.setDate(birthday)

    # Default state loader
    def resetProfileForm(self):
        self.loadProfile()
        self.ui.EditDetailsButton.setEnabled(True)
        self.ui.SaveButton.setEnabled(False)
        self.ui.CancelButton.setEnabled(False)
        self.ui.lineFirstName.setReadOnly(True)
        self.ui.lineSurname.setReadOnly(True)
        self.ui.lineEmail.setReadOnly(True)
        self.ui.dateBirthday.setReadOnly(True)

    # Save profile detail changes on database
    def saveChanges(self):
        # Confirmation message
        confirm = QMessageBox.question(self, "Profile Update", "Please confirm that you would like to update your profile?", QMessageBox.No | QMessageBox.Yes, QMessageBox.No)

        # Save information to database
        if confirm == QMessageBox.Yes:
            firstName = self.ui.lineFirstName.text()
            surname = self.ui.lineSurname.text()
            email = self.ui.lineEmail.text()
            birthday = self.ui.dateBirthday.date().toString("yyyy-MM-dd")
            query = QSqlQuery()
            query.prepare("UPDATE users SET first_name = ?, surname = ?, email = ?, dob = ? WHERE user_id = ?")
            query.addBindValue(firstName)
            query.addBindValue(surname)
            query.addBindValue(email)
            query.addBindValue(birthday)
            query.addBindValue(self.userID)
            if query.exec():
                QMessageBox.information(self, "Updated successfully", "Profile details were updated successfully.")
            else:
                QMessageBox.warning(self, "Update failed", "Failed to update profile details.")
            self.resetProfileForm()
    
    # Set window state to edit mode
    def enableEdit(self):
        self.ui.EditDetailsButton.setEnabled(False)
        self.ui.SaveButton.setEnabled(True)
        self.ui.CancelButton.setEnabled(True)
        self.ui.lineFirstName.setReadOnly(False)
        self.ui.lineSurname.setReadOnly(False)
        self.ui.lineEmail.setReadOnly(False)
        self.ui.dateBirthday.setReadOnly(False)

    # Edit profile photo function
    def editProfilePhoto(self):
        # Prompt user to select a photo from device
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Select Profile Photo", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if not filePath:
            # Display warning if file couldn't be opened
            QMessageBox.critical(self, "File not found", "Error: The selected file could not be loaded. Please try again.", QMessageBox.Ok, QMessageBox.Ok)
            return
        
        # Save image in directory and display on profile page
        picturesDir = os.path.join(os.path.dirname(__file__), "resources/assets/images/usrs")
        os.makedirs(picturesDir, exist_ok=True)
        ext = os.path.splitext(filePath)[1]
        destFilename = self.userID + ext
        destPath = os.path.join(picturesDir, destFilename)
        shutil.copy(filePath, destPath)
        self.loadProfilePhoto()
    
    # Remove profile photo from user account
    def clearProfilePhoto(self):
        confirm = QMessageBox.question(self, "Clear profile photo", "Are you sure you want to remove your profile photo?", QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            picturesDir = os.path.join(os.path.dirname(__file__), "resources/assets/images/usrs")
            for ext in (".jpg", ".png", ".jpeg"):
                pictureName = self.userID + ext
                user_photo = os.path.join(picturesDir, pictureName)
                if os.path.exists(user_photo):
                    os.remove(user_photo)
            self.loadProfilePhoto()
