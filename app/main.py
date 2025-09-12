#!/usr/bin/env python3
"""
Student Assistant Application Main Entry Point

This is a PyQt5-based desktop application for managing student assignments and grades.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class StudentrMainWindow(QMainWindow):
    """Main window for the Student Assistant application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("the-studentr - Student Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Add welcome label
        welcome_label = QLabel("Welcome to the-studentr\nStudent Assignment & Grade Manager")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(welcome_label)
        
        # Add status label
        status_label = QLabel("Application is starting...\nThis is a development build.")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("font-size: 12px; color: gray; margin: 10px;")
        layout.addWidget(status_label)

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("the-studentr")
    app.setOrganizationName("Student Tools")
    
    # Create and show main window
    window = StudentrMainWindow()
    window.show()
    
    # Run application
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())