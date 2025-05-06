import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QTabWidget, QLabel, QTabBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from login import LoginWindow

class WelcomeTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Welcome message
        welcome_label = QLabel("¡Bienvenido al Sistema de Gestión!")
        welcome_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        subtitle_label = QLabel("Seleccione una opción del menú para comenzar")
        subtitle_label.setStyleSheet("""
            font-size: 16px;
            color: #7f8c8d;
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(welcome_label)
        layout.addWidget(subtitle_label)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create left menu
        menu_widget = QWidget()
        menu_widget.setFixedWidth(200)
        menu_widget.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
            }
            QPushButton {
                text-align: left;
                padding: 15px;
                border: none;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
            }
        """)
        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setSpacing(0)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add menu buttons
        self.menu_buttons = {}
        menu_items = ["Inventario", "Clientes", "Generar Factura", "Ventas"]
        
        for item in menu_items:
            btn = QPushButton(item)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, text=item: self.open_tab(text))
            self.menu_buttons[item] = btn
            menu_layout.addWidget(btn)
        
        menu_layout.addStretch()
        
        # Create tab widget for content
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background-color: #34495e;
                color: white;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::close-button {
                image: url("icons/close.png");
                background: #34495e;
                border-radius: 8px;
                padding: 2px;
            }
            QTabBar::close-button:hover {
                background: #e74c3c;
            }
        """)
        
        # Add widgets to main layout
        main_layout.addWidget(menu_widget)
        main_layout.addWidget(self.tab_widget)
        
        # Add welcome tab
        welcome_tab = WelcomeTab()
        self.tab_widget.addTab(welcome_tab, "Inicio")
        self.tab_widget.tabBar().setTabButton(0, QTabBar.ButtonPosition.RightSide, None)  # Remove close button from welcome tab

    def open_tab(self, title):
        """Open a new tab or switch to existing one."""
        # Check if tab already exists
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == title:
                self.tab_widget.setCurrentIndex(i)
                return
        
        # Create new tab
        new_tab = QWidget()
        layout = QVBoxLayout(new_tab)
        layout.addWidget(QLabel(f"Contenido de {title}"))
        
        # Add tab
        index = self.tab_widget.addTab(new_tab, title)
        self.tab_widget.setCurrentIndex(index)
        
        # Update menu button states
        for btn in self.menu_buttons.values():
            btn.setChecked(btn.text() == title)

    def close_tab(self, index):
        """Close the tab at the specified index."""
        if self.tab_widget.count() > 1 and index != 0:  # Don't close welcome tab
            self.tab_widget.removeTab(index)
            # If closing the current tab, switch to welcome tab
            if index == self.tab_widget.currentIndex():
                self.tab_widget.setCurrentIndex(0)
            # Uncheck all menu buttons when returning to welcome tab
            if self.tab_widget.currentIndex() == 0:
                for btn in self.menu_buttons.values():
                    btn.setChecked(False)

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show login window
    login_window = LoginWindow()
    main_window = MainWindow()
    
    # Connect login signal to show main window
    login_window.login_successful.connect(main_window.show)
    
    # Show login window
    login_window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()


