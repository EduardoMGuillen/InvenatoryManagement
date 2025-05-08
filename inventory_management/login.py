from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

class LoginWindow(QWidget):
    # Signal to emit when login is successful
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iniciar Sesión")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                font-size: 14px;
                color: #000000;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLabel {
                color: #2c3e50;
            }
        """)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Logo/Title area
        title_label = QLabel("Sistema de Gestión")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        layout.addWidget(title_label)

        # Welcome message
        welcome_label = QLabel("Bienvenido")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("""
            font-size: 18px;
            color: #7f8c8d;
            margin-bottom: 30px;
        """)
        layout.addWidget(welcome_label)

        # Username field
        self.username = QLineEdit()
        self.username.setPlaceholderText("Usuario")
        layout.addWidget(self.username)

        # Password field
        self.password = QLineEdit()
        self.password.setPlaceholderText("Contraseña")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        # Login button
        login_button = QPushButton("Iniciar Sesión")
        login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        login_button.clicked.connect(self.try_login)
        layout.addWidget(login_button)

        # Add some spacing
        layout.addStretch()

        # Footer
        footer_label = QLabel("© 2024 Sistema de Gestión")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #95a5a6;")
        layout.addWidget(footer_label)

    def try_login(self):
        # TODO: Implement actual authentication
        # For now, just accept any non-empty username/password
        if self.username.text() and self.password.text():
            self.login_successful.emit()
            self.close() 