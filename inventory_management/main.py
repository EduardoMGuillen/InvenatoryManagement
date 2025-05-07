import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QTabWidget, QLabel, QTabBar,
                            QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFormLayout, QSpinBox, QDoubleSpinBox, 
                            QStyledItemDelegate, QDialog, QDateEdit, QScrollArea, QGroupBox, 
                            QCheckBox, QColorDialog)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QIcon, QTextDocument, QPainter, QPixmap, QColor
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from login import LoginWindow
from database import Database
from settings_manager import SettingsManager
from backup_manager import BackupManager

class CurrencyDelegate(QStyledItemDelegate):
    def displayText(self, value, locale):
        try:
            number = float(value)
            return f"LPS {number:,.2f}"
        except Exception:
            return str(value)

class InventoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Top bar with search and refresh
        top_bar = QHBoxLayout()
        
        # Search section
        search_layout = QHBoxLayout()
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar producto...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.search_bar.textChanged.connect(self.search_products)
        
        # Search type dropdown
        self.search_type = QComboBox()
        self.search_type.addItems(["Nombre", "Número de Serie", "ID"])
        self.search_type.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.search_type.currentTextChanged.connect(self.search_products)
        
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_type)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refrescar")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_products)
        
        top_bar.addLayout(search_layout)
        top_bar.addWidget(self.refresh_btn)
        top_bar.addStretch()
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Número de Serie", "Nombre del Producto",
            "Cantidad", "Costo (LPS)", "Precio (LPS)"
        ])
        
        # Set table style
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                gridline-color: #f0f0f0;
                color: #2c3e50;
            }
            QTableWidget::item {
                padding: 5px;
                color: #2c3e50;
                background: white;
            }
            QTableWidget::item:alternate {
                background: #f7f9fa;
            }
            QTableWidget::item:selected {
                background: #d0e7fa;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #e0e4ea;
                color: #2c3e50;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #bdc3c7;
                font-weight: bold;
            }
        """)
        
        # Configure table properties
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        
        # Set custom delegate for Costo and Precio columns
        currency_delegate = CurrencyDelegate(self.table)
        self.table.setItemDelegateForColumn(4, currency_delegate)
        self.table.setItemDelegateForColumn(5, currency_delegate)
        
        # Add widgets to main layout
        layout.addLayout(top_bar)
        layout.addWidget(self.table)
        
        # Load initial data
        self.load_products()
    
    def load_products(self):
        """Load all products from the database."""
        products = self.db.get_all_products()
        self.update_table(products)
    
    def search_products(self):
        """Search products based on the search term and type."""
        search_term = self.search_bar.text()
        search_type = self.search_type.currentText()
        
        if search_term:
            products = self.db.search_products(search_term, search_type)
        else:
            products = self.db.get_all_products()
        
        self.update_table(products)
    
    def update_table(self, products):
        """Update the table with the given products."""
        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            for col, value in enumerate(product):
                item = QTableWidgetItem()
                # Numeric columns: 0 (ID), 3 (Cantidad), 4 (Costo), 5 (Precio)
                if col in [0, 3]:
                    item.setData(Qt.ItemDataRole.DisplayRole, int(value))
                elif col in [4, 5]:
                    item.setData(Qt.ItemDataRole.DisplayRole, float(value))
                else:
                    item.setText(str(value))
                self.table.setItem(row, col, item)

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

class AddProductTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(15)

        # Serial Number
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Ej: SN2001")
        form_layout.addRow("Número de Serie:", self.serial_input)

        # Product Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Taladro Inalámbrico")
        form_layout.addRow("Nombre del Producto:", self.name_input)

        # Quantity
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 100000)
        form_layout.addRow("Cantidad:", self.quantity_input)

        # Cost
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0.01, 100000.00)
        self.cost_input.setPrefix("LPS ")
        self.cost_input.setDecimals(2)
        form_layout.addRow("Costo (LPS):", self.cost_input)

        # Price
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.01, 100000.00)
        self.price_input.setPrefix("LPS ")
        self.price_input.setDecimals(2)
        form_layout.addRow("Precio (LPS):", self.price_input)

        # Add Button
        self.add_btn = QPushButton("Añadir Producto")
        self.add_btn.clicked.connect(self.add_product)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #217dbb;
            }
        """)

        # Feedback label
        self.feedback = QLabel("")
        self.feedback.setStyleSheet("color: #27ae60; font-weight: bold; margin-top: 10px;")

        layout.addLayout(form_layout)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.feedback)
        layout.addStretch()

    def add_product(self):
        serial = self.serial_input.text().strip()
        name = self.name_input.text().strip()
        quantity = self.quantity_input.value()
        cost = self.cost_input.value()
        price = self.price_input.value()

        if not serial or not name or cost <= 0 or price <= 0:
            self.feedback.setText("Por favor, complete todos los campos correctamente.")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")
            return

        # Check if product exists
        existing = self.db.search_products(serial, "Número de Serie")
        if existing:
            self.feedback.setText("Error: El número de serie ya existe. Use 'Actualizar producto' para modificarlo.")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")
            return

        added = self.db.add_product(serial, name, quantity, cost, price)
        if added:
            self.feedback.setText(f"Producto '{name}' añadido exitosamente.")
            self.feedback.setStyleSheet("color: #27ae60; font-weight: bold; margin-top: 10px;")
            self.clear_form()
        else:
            self.feedback.setText("Error al añadir el producto.")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")

    def clear_form(self):
        self.serial_input.clear()
        self.name_input.clear()
        self.quantity_input.setValue(1)
        self.cost_input.setValue(0.00)
        self.price_input.setValue(0.00)

class UpdateProductTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Search section
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar producto...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.search_type = QComboBox()
        self.search_type.addItems(["Nombre", "Número de Serie", "ID"])
        self.search_type.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.search_btn = QPushButton("Buscar")
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #217dbb;
            }
        """)
        self.search_btn.clicked.connect(self.load_product)
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_type)
        search_layout.addWidget(self.search_btn)
        search_layout.addStretch()

        # Form for editing
        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.form_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.form_layout.setHorizontalSpacing(20)
        self.form_layout.setVerticalSpacing(15)

        self.id_label = QLabel("")
        self.id_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        self.serial_input = QLineEdit()
        self.name_input = QLineEdit()
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 100000)
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0.01, 100000.00)
        self.cost_input.setPrefix("LPS ")
        self.cost_input.setDecimals(2)
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.01, 100000.00)
        self.price_input.setPrefix("LPS ")
        self.price_input.setDecimals(2)

        self.form_layout.addRow("ID:", self.id_label)
        self.form_layout.addRow("Número de Serie:", self.serial_input)
        self.form_layout.addRow("Nombre del Producto:", self.name_input)
        self.form_layout.addRow("Cantidad:", self.quantity_input)
        self.form_layout.addRow("Costo (LPS):", self.cost_input)
        self.form_layout.addRow("Precio (LPS):", self.price_input)

        # Update Button
        self.update_btn = QPushButton("Actualizar Producto")
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        """)
        self.update_btn.clicked.connect(self.update_product)
        self.update_btn.setEnabled(False)

        # Feedback label
        self.feedback = QLabel("")
        self.feedback.setStyleSheet("color: #27ae60; font-weight: bold; margin-top: 10px;")

        layout.addLayout(search_layout)
        layout.addLayout(self.form_layout)
        layout.addWidget(self.update_btn)
        layout.addWidget(self.feedback)
        layout.addStretch()

    def load_product(self):
        search_term = self.search_bar.text().strip()
        search_type = self.search_type.currentText()
        if not search_term:
            self.feedback.setText("Ingrese un término de búsqueda.")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")
            self.update_btn.setEnabled(False)
            return
        products = self.db.search_products(search_term, search_type)
        if not products:
            self.feedback.setText("Producto no encontrado.")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")
            self.update_btn.setEnabled(False)
            self.clear_form()
            return
        prod = products[0]
        self.id_label.setText(str(prod[0]))
        self.serial_input.setText(prod[1])
        self.name_input.setText(prod[2])
        self.quantity_input.setValue(prod[3])
        self.cost_input.setValue(prod[4])
        self.price_input.setValue(prod[5])
        self.feedback.setText("Producto cargado. Puede editar los campos y actualizar.")
        self.feedback.setStyleSheet("color: #2980b9; font-weight: bold; margin-top: 10px;")
        self.update_btn.setEnabled(True)

    def update_product(self):
        try:
            product_id = int(self.id_label.text())
        except ValueError:
            self.feedback.setText("ID de producto inválido.")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")
            return
        serial = self.serial_input.text().strip()
        name = self.name_input.text().strip()
        quantity = self.quantity_input.value()
        cost = self.cost_input.value()
        price = self.price_input.value()
        if not serial or not name or cost <= 0 or price <= 0:
            self.feedback.setText("Por favor, complete todos los campos correctamente.")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")
            return
        updated = self.db.update_product(product_id, serial, name, quantity, cost, price)
        if updated:
            self.feedback.setText("Producto actualizado exitosamente.")
            self.feedback.setStyleSheet("color: #27ae60; font-weight: bold; margin-top: 10px;")
        else:
            self.feedback.setText("Error al actualizar el producto. ¿El número de serie ya existe?")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")

    def clear_form(self):
        self.id_label.setText("")
        self.serial_input.clear()
        self.name_input.clear()
        self.quantity_input.setValue(0)
        self.cost_input.setValue(0.00)
        self.price_input.setValue(0.00)

class ClientsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Top bar with search and refresh
        top_bar = QHBoxLayout()
        
        # Search section
        search_layout = QHBoxLayout()
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar cliente...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.search_bar.textChanged.connect(self.search_clients)
        
        # Search type dropdown
        self.search_type = QComboBox()
        self.search_type.addItems(["Nombre", "ID", "RTN"])
        self.search_type.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.search_type.currentTextChanged.connect(self.search_clients)
        
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_type)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refrescar")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_clients)
        
        top_bar.addLayout(search_layout)
        top_bar.addWidget(self.refresh_btn)
        top_bar.addStretch()
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "ID Personal", "RTN", "Teléfono", "Email", "Ciudad"
        ])
        
        # Set table style
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                gridline-color: #f0f0f0;
                color: #2c3e50;
            }
            QTableWidget::item {
                padding: 5px;
                color: #2c3e50;
                background: white;
            }
            QTableWidget::item:alternate {
                background: #f7f9fa;
            }
            QTableWidget::item:selected {
                background: #d0e7fa;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #e0e4ea;
                color: #2c3e50;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #bdc3c7;
                font-weight: bold;
            }
            QHeaderView::section:checked {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # Configure table properties
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        
        # Add widgets to main layout
        layout.addLayout(top_bar)
        layout.addWidget(self.table)
        
        # Load initial data
        self.load_clients()
    
    def load_clients(self):
        """Load all clients from the database."""
        clients = self.db.get_all_clients()
        self.update_table(clients)
    
    def search_clients(self):
        """Search clients based on the search term and type."""
        search_term = self.search_bar.text()
        search_type = self.search_type.currentText()
        
        if search_term:
            clients = self.db.search_clients(search_term, search_type)
        else:
            clients = self.db.get_all_clients()
        
        self.update_table(clients)
    
    def update_table(self, clients):
        """Update the table with the given clients."""
        self.table.setSortingEnabled(False)  # Disable sorting while updating
        self.table.setRowCount(len(clients))
        self.table.clearContents()  # Clear previous contents to avoid stale data
        for row, client in enumerate(clients):
            for col, value in enumerate(client):
                if col == 0:  # ID column
                    item = QTableWidgetItem()
                    item.setData(Qt.ItemDataRole.DisplayRole, int(value))
                else:
                    item = QTableWidgetItem(str(value) if value is not None else "")
                self.table.setItem(row, col, item)
        self.table.setSortingEnabled(True)  # Re-enable sorting

class AddClientTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(15)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Juan Pérez")
        form_layout.addRow("Nombre:", self.name_input)

        # Identity ID
        self.identity_input = QLineEdit()
        self.identity_input.setPlaceholderText("Ej: 0801-1990-12345")
        form_layout.addRow("ID Personal:", self.identity_input)

        # RTN
        self.rtn_input = QLineEdit()
        self.rtn_input.setPlaceholderText("Ej: 0801-1990-12345-00000")
        form_layout.addRow("RTN:", self.rtn_input)

        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Ej: 9999-9999")
        form_layout.addRow("Teléfono:", self.phone_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ej: juan@email.com")
        form_layout.addRow("Email:", self.email_input)

        # City
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Ej: Tegucigalpa")
        form_layout.addRow("Ciudad:", self.city_input)

        # Add Button
        self.add_btn = QPushButton("Añadir Cliente")
        self.add_btn.clicked.connect(self.add_client)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #217dbb;
            }
        """)

        # Feedback label
        self.feedback = QLabel("")
        self.feedback.setStyleSheet("color: #27ae60; font-weight: bold; margin-top: 10px;")

        layout.addLayout(form_layout)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.feedback)
        layout.addStretch()

    def add_client(self):
        name = self.name_input.text().strip()
        identity_id = self.identity_input.text().strip()
        rtn = self.rtn_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        city = self.city_input.text().strip()

        if not name or not identity_id or not city:
            self.feedback.setText("Por favor, complete los campos obligatorios (Nombre, ID Personal y Ciudad).")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")
            return

        # Check if client exists
        existing = self.db.search_clients(identity_id, "ID")
        if existing:
            self.feedback.setText("Error: El ID Personal ya existe. Use 'Actualizar cliente' para modificarlo.")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")
            return

        added = self.db.add_client(name, identity_id, rtn, phone, email, city)
        if added:
            self.feedback.setText(f"Cliente '{name}' añadido exitosamente.")
            self.feedback.setStyleSheet("color: #27ae60; font-weight: bold; margin-top: 10px;")
            self.clear_form()
        else:
            self.feedback.setText("Error al añadir el cliente. ¿El RTN ya existe?")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")

    def clear_form(self):
        self.name_input.clear()
        self.identity_input.clear()
        self.rtn_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.city_input.clear()

class UpdateClientTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Search section
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar cliente...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.search_type = QComboBox()
        self.search_type.addItems(["Nombre", "ID", "RTN"])
        self.search_type.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.search_btn = QPushButton("Buscar")
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #217dbb;
            }
        """)
        self.search_btn.clicked.connect(self.load_client)
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_type)
        search_layout.addWidget(self.search_btn)
        search_layout.addStretch()

        # Form for editing
        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.form_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.form_layout.setHorizontalSpacing(20)
        self.form_layout.setVerticalSpacing(15)

        self.id_label = QLabel("")
        self.id_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        self.name_input = QLineEdit()
        self.identity_input = QLineEdit()
        self.rtn_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.city_input = QLineEdit()

        self.form_layout.addRow("ID:", self.id_label)
        self.form_layout.addRow("Nombre:", self.name_input)
        self.form_layout.addRow("ID Personal:", self.identity_input)
        self.form_layout.addRow("RTN:", self.rtn_input)
        self.form_layout.addRow("Teléfono:", self.phone_input)
        self.form_layout.addRow("Email:", self.email_input)
        self.form_layout.addRow("Ciudad:", self.city_input)

        # Update Button
        self.update_btn = QPushButton("Actualizar Cliente")
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        """)
        self.update_btn.clicked.connect(self.update_client)
        self.update_btn.setEnabled(False)

        # Feedback label
        self.feedback = QLabel("")
        self.feedback.setStyleSheet("color: #27ae60; font-weight: bold; margin-top: 10px;")

        layout.addLayout(search_layout)
        layout.addLayout(self.form_layout)
        layout.addWidget(self.update_btn)
        layout.addWidget(self.feedback)
        layout.addStretch()

    def load_client(self):
        search_term = self.search_bar.text().strip()
        search_type = self.search_type.currentText()
        if not search_term:
            self.feedback.setText("Ingrese un término de búsqueda.")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")
            self.update_btn.setEnabled(False)
            return
        clients = self.db.search_clients(search_term, search_type)
        if not clients:
            self.feedback.setText("Cliente no encontrado.")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")
            self.update_btn.setEnabled(False)
            self.clear_form()
            return
        client = clients[0]
        self.id_label.setText(str(client[0]))
        self.name_input.setText(client[1])
        self.identity_input.setText(client[2])
        self.rtn_input.setText(client[3] if client[3] else "")
        self.phone_input.setText(client[4] if client[4] else "")
        self.email_input.setText(client[5] if client[5] else "")
        self.city_input.setText(client[6])
        self.feedback.setText("Cliente cargado. Puede editar los campos y actualizar.")
        self.feedback.setStyleSheet("color: #2980b9; font-weight: bold; margin-top: 10px;")
        self.update_btn.setEnabled(True)

    def update_client(self):
        try:
            client_id = int(self.id_label.text())
        except ValueError:
            self.feedback.setText("ID de cliente inválido.")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")
            return
        name = self.name_input.text().strip()
        identity_id = self.identity_input.text().strip()
        rtn = self.rtn_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        city = self.city_input.text().strip()

        if not name or not identity_id or not city:
            self.feedback.setText("Por favor, complete los campos obligatorios (Nombre, ID Personal y Ciudad).")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")
            return

        updated = self.db.update_client(client_id, name, identity_id, rtn, phone, email, city)
        if updated:
            self.feedback.setText("Cliente actualizado exitosamente.")
            self.feedback.setStyleSheet("color: #27ae60; font-weight: bold; margin-top: 10px;")
        else:
            self.feedback.setText("Error al actualizar el cliente. ¿El ID Personal o RTN ya existe?")
            self.feedback.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 10px;")

    def clear_form(self):
        self.id_label.setText("")
        self.name_input.clear()
        self.identity_input.clear()
        self.rtn_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.city_input.clear()

class GenerateInvoiceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        # --- Client selection ---
        client_layout = QHBoxLayout()
        self.client_combo = QComboBox()
        self.load_clients()
        client_layout.addWidget(QLabel("Cliente:"))
        client_layout.addWidget(self.client_combo)
        layout.addLayout(client_layout)
        # --- Product selection table ---
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Número de Serie", "Precio (LPS)", "Disponible", "Cantidad"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.products_table.setAlternatingRowColors(True)
        layout.addWidget(self.products_table)
        # --- Add to invoice button ---
        self.add_btn = QPushButton("Agregar a Factura")
        self.add_btn.clicked.connect(self.add_to_invoice)
        layout.addWidget(self.add_btn)
        # --- Invoice preview ---
        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(5)
        self.invoice_table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Cantidad", "Precio Unitario", "Subtotal"
        ])
        self.invoice_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.invoice_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.invoice_table.setAlternatingRowColors(True)
        layout.addWidget(self.invoice_table)
        # --- Totals ---
        totals_layout = QHBoxLayout()
        self.subtotal_label = QLabel("Subtotal: LPS 0.00")
        self.tax_label = QLabel("ISV (15%): LPS 0.00")
        self.total_label = QLabel("Total: LPS 0.00")
        totals_layout.addWidget(self.subtotal_label)
        totals_layout.addWidget(self.tax_label)
        totals_layout.addWidget(self.total_label)
        totals_layout.addStretch()
        layout.addLayout(totals_layout)
        # --- Generate invoice button ---
        self.generate_btn = QPushButton("Generar Factura")
        self.generate_btn.clicked.connect(self.generate_invoice)
        layout.addWidget(self.generate_btn)
        # --- Feedback ---
        self.feedback = QLabel("")
        layout.addWidget(self.feedback)
        self.setLayout(layout)
        self.selected_products = []  # (product_id, name, serial, qty, price, subtotal)
        self.load_products()
    def load_clients(self):
        self.client_combo.clear()
        clients = self.db.get_all_clients()
        for c in clients:
            self.client_combo.addItem(f"{c[1]} (ID: {c[0]})", c[0])
    def load_products(self):
        self.products_table.setRowCount(0)
        products = self.db.get_all_products()
        for row, prod in enumerate(products):
            self.products_table.insertRow(row)
            # prod: (id, serial_number, name, quantity, cost, price)
            # Table columns: ID, Nombre, Número de Serie, Precio (LPS), Disponible, Cantidad
            self.products_table.setItem(row, 0, QTableWidgetItem(str(prod[0])))  # ID
            self.products_table.setItem(row, 1, QTableWidgetItem(prod[2]))       # Nombre
            self.products_table.setItem(row, 2, QTableWidgetItem(prod[1]))       # Número de Serie
            self.products_table.setItem(row, 3, QTableWidgetItem(f"{prod[5]:.2f}"))  # Precio (LPS)
            self.products_table.setItem(row, 4, QTableWidgetItem(str(prod[3])))  # Disponible
            spin = QSpinBox()
            spin.setRange(0, int(prod[3]))
            self.products_table.setCellWidget(row, 5, spin)
    def add_to_invoice(self):
        # Add selected products to invoice preview, now including serial number
        for row in range(self.products_table.rowCount()):
            spin = self.products_table.cellWidget(row, 5)
            qty = spin.value()
            if qty > 0:
                prod_id = int(self.products_table.item(row, 0).text())
                name = self.products_table.item(row, 1).text()
                serial = self.products_table.item(row, 2).text()
                price = float(self.products_table.item(row, 3).text())
                subtotal = qty * price
                # Check if product already in selected_products
                found = False
                for i, (pid, n, s, q, p, sub) in enumerate(self.selected_products):
                    if pid == prod_id and s == serial:
                        # Update quantity and subtotal
                        new_qty = q + qty
                        new_sub = new_qty * price
                        self.selected_products[i] = (pid, n, s, new_qty, p, new_sub)
                        found = True
                        break
                if not found:
                    self.selected_products.append((prod_id, name, serial, qty, price, subtotal))
                spin.setValue(0)
        self.update_invoice_table()
    def update_invoice_table(self):
        # Update invoice preview table to include serial number
        self.invoice_table.setColumnCount(6)
        self.invoice_table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Número de Serie", "Cantidad", "Precio Unitario", "Subtotal"
        ])
        self.invoice_table.setRowCount(len(self.selected_products))
        subtotal = 0
        for row, (prod_id, name, serial, qty, price, sub) in enumerate(self.selected_products):
            self.invoice_table.setItem(row, 0, QTableWidgetItem(str(prod_id)))
            self.invoice_table.setItem(row, 1, QTableWidgetItem(name))
            self.invoice_table.setItem(row, 2, QTableWidgetItem(serial))
            self.invoice_table.setItem(row, 3, QTableWidgetItem(str(qty)))
            self.invoice_table.setItem(row, 4, QTableWidgetItem(f"LPS {price:.2f}"))
            self.invoice_table.setItem(row, 5, QTableWidgetItem(f"LPS {sub:.2f}"))
            subtotal += sub
        tax = subtotal * 0.15
        total = subtotal + tax
        self.subtotal_label.setText(f"Subtotal: LPS {subtotal:.2f}")
        self.tax_label.setText(f"ISV (15%): LPS {tax:.2f}")
        self.total_label.setText(f"Total: LPS {total:.2f}")
    def generate_invoice(self):
        import datetime, os
        if not self.selected_products:
            self.feedback.setText("Seleccione productos para la factura.")
            return
        client_index = self.client_combo.currentIndex()
        client_id = self.client_combo.itemData(client_index)
        client_name = self.client_combo.currentText().split(' (ID:')[0]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subtotal = sum(sub for *_, sub in self.selected_products)
        tax = subtotal * 0.15
        total = subtotal + tax
        # Generate invoice text
        # First, get a new invoice ID by checking the max ID in the DB
        import sqlite3
        with sqlite3.connect(self.db.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(id) FROM invoices")
            row = cursor.fetchone()
            invoice_id = (row[0] or 0) + 1
        filename = f"invoices/invoice_{invoice_id:05d}.txt"
        lines = [
            f"Factura N°: {invoice_id}",
            f"Fecha: {now}",
            f"Cliente: {client_name} (ID: {client_id})",
            "\nDetalle de productos:",
            f"{'Cantidad':<10}{'Nombre':<30}{'N° Serie':<15}{'Precio':<15}{'Subtotal':<15}",
            "-"*85
        ]
        for prod_id, name, serial, qty, price, sub in self.selected_products:
            lines.append(f"{qty:<10}{name:<30}{serial:<15}LPS {price:<12.2f}LPS {sub:<12.2f}")
        lines += [
            "\n",
            f"{'Subtotal:':<20}LPS {subtotal:.2f}",
            f"{'ISV (15%):':<20}LPS {tax:.2f}",
            f"{'Total:':<20}LPS {total:.2f}"
        ]
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        # Now add invoice record with correct file path
        self.db.add_invoice(client_id, client_name, now, subtotal, tax, total, filename)
        self.feedback.setText(f"Factura generada: {filename}")
        self.selected_products.clear()
        self.update_invoice_table()

class ManageInvoicesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Search section
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar factura...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.search_bar.textChanged.connect(self.search_invoices)
        self.search_type = QComboBox()
        self.search_type.addItems(["Cliente", "ID Factura"])
        self.search_type.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.search_type.currentTextChanged.connect(self.search_invoices)
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_type)
        self.refresh_btn = QPushButton("Refrescar")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_invoices)
        search_layout.addWidget(self.refresh_btn)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Fecha", "Subtotal", "ISV", "Total"
        ])
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                gridline-color: #f0f0f0;
                color: #2c3e50;
            }
            QTableWidget::item {
                padding: 5px;
                color: #2c3e50;
                background: white;
            }
            QTableWidget::item:alternate {
                background: #f7f9fa;
            }
            QTableWidget::item:selected {
                background: #d0e7fa;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #e0e4ea;
                color: #2c3e50;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #bdc3c7;
                font-weight: bold;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        # Action buttons (single set)
        btn_layout = QHBoxLayout()
        self.view_btn = QPushButton("Ver")
        self.view_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1c5d99;
            }
        """)
        self.view_btn.clicked.connect(self.view_invoice)
        btn_layout.addWidget(self.view_btn)
        self.print_btn = QPushButton("Imprimir")
        self.print_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #217dbb;
            }
        """)
        self.print_btn.clicked.connect(self.print_invoice)
        btn_layout.addWidget(self.print_btn)
        self.delete_btn = QPushButton("Eliminar")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_invoice)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        # Invoice display (white canvas)
        self.invoice_display = QLabel("")
        self.invoice_display.setStyleSheet("""
            QLabel {
                background: #fff;
                border: 1px solid #ccc;
                padding: 20px;
                font-family: monospace;
                color: #222;
                min-height: 200px;
            }
        """)
        self.invoice_display.setWordWrap(True)
        layout.addWidget(self.invoice_display)
        self.setLayout(layout)
        self.load_invoices()
    def load_invoices(self):
        invoices = self.db.get_all_invoices()
        self.update_table(invoices)
    def search_invoices(self):
        search_term = self.search_bar.text()
        search_type = self.search_type.currentText()
        if search_term:
            invoices = self.db.search_invoices(search_term, search_type)
        else:
            invoices = self.db.get_all_invoices()
        self.update_table(invoices)
    def update_table(self, invoices):
        self.table.setRowCount(len(invoices))
        self.table.clearContents()
        for row, invoice in enumerate(invoices):
            for col, value in enumerate(invoice[:-1]):  # Exclude file_path
                item = QTableWidgetItem()
                if col == 0:  # ID
                    item.setData(Qt.ItemDataRole.DisplayRole, int(value))
                elif col == 2:  # Date
                    item.setText(str(value))
                elif col in [3, 4, 5]:  # Subtotal, ISV, Total
                    try:
                        float_value = float(value)
                        item.setData(Qt.ItemDataRole.DisplayRole, float_value)
                        item.setText(f"LPS {float_value:,.2f}")
                    except (ValueError, TypeError):
                        item.setText(str(value))
                else:  # Client name
                    item.setText(str(value))
                self.table.setItem(row, col, item)
    def get_selected_invoice(self):
        selected = self.table.currentRow()
        if selected < 0:
            return None
        # Get the invoice ID from the first column
        invoice_id = int(self.table.item(selected, 0).text())
        invoice = self.db.get_invoice_by_id(invoice_id)
        return invoice
    def view_invoice(self):
        invoice = self.get_selected_invoice()
        if not invoice:
            self.invoice_display.setText("Seleccione una factura para ver.")
            return
        file_path = invoice[-1]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.invoice_display.setText(content)
        except Exception as e:
            self.invoice_display.setText(f"No se pudo abrir la factura: {e}")
    def print_invoice(self):
        invoice = self.get_selected_invoice()
        if not invoice:
            QMessageBox.warning(self, "Imprimir", "Seleccione una factura para imprimir.")
            return
        file_path = invoice[-1]
        try:
            # Load invoice text
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Parse invoice data from text (simple parsing for demo)
            lines = content.splitlines()
            factura_num = lines[0].split(':', 1)[-1].strip()
            fecha = lines[1].split(':', 1)[-1].strip()
            cliente = lines[2].split(':', 1)[-1].strip()
            # Find product table start
            prod_start = 5
            prod_lines = []
            for i in range(prod_start+1, len(lines)):
                if lines[i].strip() == '':
                    break
                prod_lines.append(lines[i])
            # Totals
            subtotal = lines[-3].split(':', 1)[-1].strip()
            isv = lines[-2].split(':', 1)[-1].strip()
            total = lines[-1].split(':', 1)[-1].strip()
            # Build HTML
            html = f'''
            <html>
            <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #222; }}
                .header {{ font-size: 22px; font-weight: bold; margin-bottom: 10px; }}
                .meta {{ margin-bottom: 10px; }}
                .meta span {{ margin-right: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
                th {{ background: #f0f0f0; }}
                .totals td {{ border: none; font-size: 16px; }}
                .totals tr td:first-child {{ text-align: right; }}
            </style>
            </head>
            <body>
                <div class="header">Factura N°: {factura_num}</div>
                <div class="meta">
                    <span><b>Fecha:</b> {fecha}</span>
                    <span><b>Cliente:</b> {cliente}</span>
                </div>
                <table>
                    <tr><th>Cantidad</th><th>Nombre</th><th>N° Serie</th><th>Precio</th><th>Subtotal</th></tr>
            '''
            for prod in prod_lines:
                cols = prod.split()
                if len(cols) < 5:
                    continue
                qty = cols[0]
                name = ' '.join(cols[1:-3])
                serial = cols[-3]
                price = cols[-2] + ' ' + cols[-1] if cols[-2].startswith('LPS') else cols[-2]
                subtotal = cols[-1] if cols[-1].startswith('LPS') else ''
                html += f'<tr><td>{qty}</td><td>{name}</td><td>{serial}</td><td>{price}</td><td>{subtotal}</td></tr>'
            html += f'''
                </table>
                <table class="totals">
                    <tr><td><b>Subtotal:</b></td><td>{subtotal}</td></tr>
                    <tr><td><b>ISV (15%):</b></td><td>{isv}</td></tr>
                    <tr><td><b>Total:</b></td><td>{total}</td></tr>
                </table>
            </body>
            </html>
            '''
            doc = QTextDocument()
            doc.setHtml(html)
            printer = QPrinter()
            dialog = QPrintDialog(printer)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                painter = QPainter(printer)
                doc.drawContents(painter)
                painter.end()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al imprimir la factura: {str(e)}")
    def delete_invoice(self):
        invoice = self.get_selected_invoice()
        if not invoice:
            QMessageBox.warning(self, "Eliminar", "Seleccione una factura para eliminar.")
            return
        reply = QMessageBox.question(
            self, 'Confirmar eliminación',
            f'¿Está seguro que desea eliminar la factura #{invoice[0]}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                import os
                file_path = invoice[-1]
                if os.path.exists(file_path):
                    os.remove(file_path)
                if self.db.delete_invoice(invoice[0]):
                    self.load_invoices()
                    self.invoice_display.setText("")
                    QMessageBox.information(self, "Éxito", "Factura eliminada correctamente.")
                else:
                    QMessageBox.critical(self, "Error", "Error al eliminar la factura de la base de datos.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar la factura: {str(e)}")

class SalesReportTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        # --- Filters ---
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Fecha inicio:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("Fecha fin:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date)
        self.generate_btn = QPushButton("Generar Reporte")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1c5d99;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_report)
        self.print_btn = QPushButton("Imprimir Reporte")
        self.print_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #217dbb;
            }
        """)
        self.print_btn.clicked.connect(self.print_report)
        filter_layout.addWidget(self.generate_btn)
        filter_layout.addWidget(self.print_btn)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        # --- Results table ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID Factura", "Cliente", "Fecha", "Subtotal", "ISV", "Total"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        # --- Summary ---
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-size: 15px; color: #fff; padding: 10px;")
        layout.addWidget(self.summary_label)
        self.setLayout(layout)
        self.current_report = []
        self.current_total = 0
    def generate_report(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        invoices = self.db.get_invoices_by_date_range(start, end)
        self.current_report = invoices
        self.table.setRowCount(len(invoices))
        total_sales = 0
        for row, inv in enumerate(invoices):
            for col, value in enumerate(inv[:6]):
                item = QTableWidgetItem()
                if col == 0:
                    item.setData(Qt.ItemDataRole.DisplayRole, int(value))
                elif col == 2:
                    item.setText(str(value))
                elif col in [3, 4, 5]:
                    try:
                        float_value = float(value)
                        item.setData(Qt.ItemDataRole.DisplayRole, float_value)
                        item.setText(f"LPS {float_value:,.2f}")
                        if col == 5:
                            total_sales += float_value
                    except (ValueError, TypeError):
                        item.setText(str(value))
                else:
                    item.setText(str(value))
                self.table.setItem(row, col, item)
        self.current_total = total_sales
        self.summary_label.setText(f"Total de facturas: {len(invoices)} | Ventas totales: LPS {total_sales:,.2f}")
    def print_report(self):
        from PyQt6.QtGui import QTextDocument, QPainter
        from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        invoices = self.current_report
        total_sales = self.current_total
        html = f'''
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #222; }}
            .header {{ font-size: 22px; font-weight: bold; margin-bottom: 10px; }}
            .meta {{ margin-bottom: 10px; }}
            .meta span {{ margin-right: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
            th {{ background: #f0f0f0; }}
            .totals td {{ border: none; font-size: 16px; }}
            .totals tr td:first-child {{ text-align: right; }}
        </style>
        </head>
        <body>
            <div class="header">Reporte de Ventas</div>
            <div class="meta">
                <span><b>Del:</b> {start}</span>
                <span><b>Al:</b> {end}</span>
            </div>
            <table>
                <tr><th>ID Factura</th><th>Cliente</th><th>Fecha</th><th>Subtotal</th><th>ISV</th><th>Total</th></tr>
        '''
        for inv in invoices:
            html += f'<tr>'
            html += f'<td>{inv[0]}</td>'
            html += f'<td>{inv[2]}</td>'
            html += f'<td>{inv[3]}</td>'
            html += f'<td>LPS {float(inv[4]):,.2f}</td>'
            html += f'<td>LPS {float(inv[5]):,.2f}</td>'
            html += f'<td>LPS {float(inv[6]):,.2f}</td>'
            html += f'</tr>'
        html += f'''
            </table>
            <table class="totals">
                <tr><td><b>Total de facturas:</b></td><td>{len(invoices)}</td></tr>
                <tr><td><b>Ventas totales:</b></td><td>LPS {total_sales:,.2f}</td></tr>
            </table>
        </body>
        </html>
        '''
        doc = QTextDocument()
        doc.setHtml(html)
        printer = QPrinter()
        dialog = QPrintDialog(printer)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            painter = QPainter(printer)
            doc.drawContents(painter)
            painter.end()

class PurchaseHistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        # --- Client selector ---
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Cliente:"))
        self.client_combo = QComboBox()
        self.load_clients()
        filter_layout.addWidget(self.client_combo)
        self.generate_btn = QPushButton("Ver Historial")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1c5d99;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_history)
        filter_layout.addWidget(self.generate_btn)
        self.print_btn = QPushButton("Imprimir Historial")
        self.print_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #217dbb;
            }
        """)
        self.print_btn.clicked.connect(self.print_history)
        filter_layout.addWidget(self.print_btn)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        # --- Results table ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID Factura", "Cliente", "Fecha", "Subtotal", "ISV", "Total"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        # --- Summary ---
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-size: 15px; color: #fff; padding: 10px;")
        layout.addWidget(self.summary_label)
        self.setLayout(layout)
        self.current_history = []
        self.current_total = 0
    def load_clients(self):
        self.client_combo.clear()
        clients = self.db.get_all_clients()
        for c in clients:
            self.client_combo.addItem(f"{c[1]} (ID: {c[0]})", c[0])
    def generate_history(self):
        client_index = self.client_combo.currentIndex()
        client_id = self.client_combo.itemData(client_index)
        invoices = self.db.get_invoices_by_client(client_id)
        self.current_history = invoices
        self.table.setRowCount(len(invoices))
        total_spent = 0
        for row, inv in enumerate(invoices):
            for col, value in enumerate(inv[:6]):
                item = QTableWidgetItem()
                if col == 0:
                    item.setData(Qt.ItemDataRole.DisplayRole, int(value))
                elif col == 2:
                    item.setText(str(value))
                elif col in [3, 4, 5]:
                    try:
                        float_value = float(value)
                        item.setData(Qt.ItemDataRole.DisplayRole, float_value)
                        item.setText(f"LPS {float_value:,.2f}")
                        if col == 5:
                            total_spent += float_value
                    except (ValueError, TypeError):
                        item.setText(str(value))
                else:
                    item.setText(str(value))
                self.table.setItem(row, col, item)
        self.current_total = total_spent
        self.summary_label.setText(f"Total de compras: {len(invoices)} | Total gastado: LPS {total_spent:,.2f}")
    def print_history(self):
        from PyQt6.QtGui import QTextDocument, QPainter
        from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
        client_index = self.client_combo.currentIndex()
        client_name = self.client_combo.currentText()
        invoices = self.current_history
        total_spent = self.current_total
        html = f'''
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #222; }}
            .header {{ font-size: 22px; font-weight: bold; margin-bottom: 10px; }}
            .meta {{ margin-bottom: 10px; }}
            .meta span {{ margin-right: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
            th {{ background: #f0f0f0; }}
            .totals td {{ border: none; font-size: 16px; }}
            .totals tr td:first-child {{ text-align: right; }}
        </style>
        </head>
        <body>
            <div class="header">Historial de Compras</div>
            <div class="meta">
                <span><b>Cliente:</b> {client_name}</span>
            </div>
            <table>
                <tr><th>ID Factura</th><th>Cliente</th><th>Fecha</th><th>Subtotal</th><th>ISV</th><th>Total</th></tr>
        '''
        for inv in invoices:
            html += f'<tr>'
            html += f'<td>{inv[0]}</td>'
            html += f'<td>{inv[2]}</td>'
            html += f'<td>{inv[3]}</td>'
            html += f'<td>LPS {float(inv[4]):,.2f}</td>'
            html += f'<td>LPS {float(inv[5]):,.2f}</td>'
            html += f'<td>LPS {float(inv[6]):,.2f}</td>'
            html += f'</tr>'
        html += f'''
            </table>
            <table class="totals">
                <tr><td><b>Total de compras:</b></td><td>{len(invoices)}</td></tr>
                <tr><td><b>Total gastado:</b></td><td>LPS {total_spent:,.2f}</td></tr>
            </table>
        </body>
        </html>
        '''
        doc = QTextDocument()
        doc.setHtml(html)
        printer = QPrinter()
        dialog = QPrintDialog(printer)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            painter = QPainter(printer)
            doc.drawContents(painter)
            painter.end()

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Create scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Create container widget for settings
        settings_container = QWidget()
        settings_layout = QVBoxLayout(settings_container)
        settings_layout.setSpacing(20)

        # Appearance Section
        appearance_group = self.create_group_box("Apariencia")
        appearance_layout = QFormLayout()
        
        # Theme selector
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Claro", "Oscuro"])
        self.theme_combo.setCurrentText("Claro" if self.settings_manager.get_setting("theme") == "light" else "Oscuro")
        self.theme_combo.currentTextChanged.connect(lambda t: self.settings_manager.set_setting("theme", "light" if t == "Claro" else "dark"))
        appearance_layout.addRow("Tema:", self.theme_combo)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 20)
        self.font_size_spin.setValue(self.settings_manager.get_setting("font_size"))
        self.font_size_spin.valueChanged.connect(lambda v: self.settings_manager.set_setting("font_size", v))
        appearance_layout.addRow("Tamaño de fuente:", self.font_size_spin)
        
        # Accent color
        self.color_button = QPushButton()
        self.color_button.setStyleSheet(f"background-color: {self.settings_manager.get_setting('accent_color')}; min-width: 100px;")
        self.color_button.clicked.connect(self.choose_color)
        appearance_layout.addRow("Color de acento:", self.color_button)
        
        appearance_group.setLayout(appearance_layout)
        settings_layout.addWidget(appearance_group)

        # Company Information Section
        company_group = self.create_group_box("Información de la Empresa")
        company_layout = QFormLayout()
        
        # Company name
        self.company_name = QLineEdit(self.settings_manager.get_setting("company_name"))
        self.company_name.textChanged.connect(lambda t: self.settings_manager.set_setting("company_name", t))
        company_layout.addRow("Nombre:", self.company_name)
        
        # Company address
        self.company_address = QLineEdit(self.settings_manager.get_setting("company_address"))
        self.company_address.textChanged.connect(lambda t: self.settings_manager.set_setting("company_address", t))
        company_layout.addRow("Dirección:", self.company_address)
        
        # Company phone
        self.company_phone = QLineEdit(self.settings_manager.get_setting("company_phone"))
        self.company_phone.textChanged.connect(lambda t: self.settings_manager.set_setting("company_phone", t))
        company_layout.addRow("Teléfono:", self.company_phone)
        
        # Company email
        self.company_email = QLineEdit(self.settings_manager.get_setting("company_email"))
        self.company_email.textChanged.connect(lambda t: self.settings_manager.set_setting("company_email", t))
        company_layout.addRow("Email:", self.company_email)
        
        # Company RTN
        self.company_rtn = QLineEdit(self.settings_manager.get_setting("company_rtn"))
        self.company_rtn.textChanged.connect(lambda t: self.settings_manager.set_setting("company_rtn", t))
        company_layout.addRow("RTN:", self.company_rtn)
        
        company_group.setLayout(company_layout)
        settings_layout.addWidget(company_group)

        # Invoice Settings Section
        invoice_group = self.create_group_box("Configuración de Facturas")
        invoice_layout = QFormLayout()
        
        # Tax rate
        self.tax_rate = QDoubleSpinBox()
        self.tax_rate.setRange(0, 100)
        self.tax_rate.setValue(self.settings_manager.get_setting("tax_rate"))
        self.tax_rate.valueChanged.connect(lambda v: self.settings_manager.set_setting("tax_rate", v))
        invoice_layout.addRow("Tasa de impuesto (%):", self.tax_rate)
        
        # Invoice prefix
        self.invoice_prefix = QLineEdit(self.settings_manager.get_setting("invoice_prefix"))
        self.invoice_prefix.textChanged.connect(lambda t: self.settings_manager.set_setting("invoice_prefix", t))
        invoice_layout.addRow("Prefijo de factura:", self.invoice_prefix)
        
        invoice_group.setLayout(invoice_layout)
        settings_layout.addWidget(invoice_group)

        # Database Settings Section
        database_group = self.create_group_box("Configuración de Base de Datos")
        database_layout = QFormLayout()
        
        # Backup enabled
        self.backup_enabled = QCheckBox()
        self.backup_enabled.setChecked(self.settings_manager.get_setting("backup_enabled"))
        self.backup_enabled.stateChanged.connect(lambda s: self.settings_manager.set_setting("backup_enabled", bool(s)))
        database_layout.addRow("Habilitar respaldo automático:", self.backup_enabled)
        
        # Backup interval
        self.backup_interval = QSpinBox()
        self.backup_interval.setRange(1, 30)
        self.backup_interval.setValue(self.settings_manager.get_setting("backup_interval_days"))
        self.backup_interval.valueChanged.connect(lambda v: self.settings_manager.set_setting("backup_interval_days", v))
        database_layout.addRow("Intervalo de respaldo (días):", self.backup_interval)
        
        # Backup folder
        self.backup_folder = QLineEdit(self.settings_manager.get_setting("backup_folder"))
        self.backup_folder.textChanged.connect(lambda t: self.settings_manager.set_setting("backup_folder", t))
        database_layout.addRow("Carpeta de respaldo:", self.backup_folder)
        
        database_group.setLayout(database_layout)
        settings_layout.addWidget(database_group)

        # Default Values Section
        defaults_group = self.create_group_box("Valores Predeterminados")
        defaults_layout = QFormLayout()
        
        # Default product quantity
        self.default_quantity = QSpinBox()
        self.default_quantity.setRange(1, 1000)
        self.default_quantity.setValue(self.settings_manager.get_setting("default_product_quantity"))
        self.default_quantity.valueChanged.connect(lambda v: self.settings_manager.set_setting("default_product_quantity", v))
        defaults_layout.addRow("Cantidad predeterminada:", self.default_quantity)
        
        # Default product cost
        self.default_cost = QDoubleSpinBox()
        self.default_cost.setRange(0, 1000000)
        self.default_cost.setValue(self.settings_manager.get_setting("default_product_cost"))
        self.default_cost.valueChanged.connect(lambda v: self.settings_manager.set_setting("default_product_cost", v))
        defaults_layout.addRow("Costo predeterminado:", self.default_cost)
        
        # Default product price
        self.default_price = QDoubleSpinBox()
        self.default_price.setRange(0, 1000000)
        self.default_price.setValue(self.settings_manager.get_setting("default_product_price"))
        self.default_price.valueChanged.connect(lambda v: self.settings_manager.set_setting("default_product_price", v))
        defaults_layout.addRow("Precio predeterminado:", self.default_price)
        
        defaults_group.setLayout(defaults_layout)
        settings_layout.addWidget(defaults_group)

        # Language Section
        language_group = self.create_group_box("Idioma")
        language_layout = QFormLayout()
        
        # Language selector
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Español", "English"])
        self.language_combo.setCurrentText("Español" if self.settings_manager.get_setting("language") == "es" else "English")
        self.language_combo.currentTextChanged.connect(lambda t: self.settings_manager.set_setting("language", "es" if t == "Español" else "en"))
        language_layout.addRow("Idioma:", self.language_combo)
        
        language_group.setLayout(language_layout)
        settings_layout.addWidget(language_group)

        # Auto-save Section
        autosave_group = self.create_group_box("Auto-guardado")
        autosave_layout = QFormLayout()
        
        # Auto-save enabled
        self.autosave_enabled = QCheckBox()
        self.autosave_enabled.setChecked(self.settings_manager.get_setting("auto_save_enabled"))
        self.autosave_enabled.stateChanged.connect(lambda s: self.settings_manager.set_setting("auto_save_enabled", bool(s)))
        autosave_layout.addRow("Habilitar auto-guardado:", self.autosave_enabled)
        
        # Auto-save interval
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(1, 60)
        self.autosave_interval.setValue(self.settings_manager.get_setting("auto_save_interval_minutes"))
        self.autosave_interval.valueChanged.connect(lambda v: self.settings_manager.set_setting("auto_save_interval_minutes", v))
        autosave_layout.addRow("Intervalo de auto-guardado (minutos):", self.autosave_interval)
        
        autosave_group.setLayout(autosave_layout)
        settings_layout.addWidget(autosave_group)

        # Reset button
        reset_btn = QPushButton("Restaurar valores predeterminados")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        reset_btn.clicked.connect(self.reset_settings)
        settings_layout.addWidget(reset_btn)

        # Add stretch to push everything to the top
        settings_layout.addStretch()

        # Set the scroll area's widget
        scroll.setWidget(settings_container)
        layout.addWidget(scroll)

    def create_group_box(self, title):
        """Create a styled group box for settings sections."""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        return group

    def choose_color(self):
        """Open color picker dialog for accent color."""
        color = QColorDialog.getColor(QColor(self.settings_manager.get_setting("accent_color")))
        if color.isValid():
            self.settings_manager.set_setting("accent_color", color.name())
            self.color_button.setStyleSheet(f"background-color: {color.name()}; min-width: 100px;")

    def reset_settings(self):
        """Reset all settings to default values."""
        reply = QMessageBox.question(
            self,
            "Confirmar restablecimiento",
            "¿Está seguro que desea restablecer todas las configuraciones a sus valores predeterminados?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings_manager.reset_to_defaults()
            # Refresh all UI elements with new values
            self.theme_combo.setCurrentText("Claro" if self.settings_manager.get_setting("theme") == "light" else "Oscuro")
            self.font_size_spin.setValue(self.settings_manager.get_setting("font_size"))
            self.color_button.setStyleSheet(f"background-color: {self.settings_manager.get_setting('accent_color')}; min-width: 100px;")
            self.company_name.setText(self.settings_manager.get_setting("company_name"))
            self.company_address.setText(self.settings_manager.get_setting("company_address"))
            self.company_phone.setText(self.settings_manager.get_setting("company_phone"))
            self.company_email.setText(self.settings_manager.get_setting("company_email"))
            self.company_rtn.setText(self.settings_manager.get_setting("company_rtn"))
            self.tax_rate.setValue(self.settings_manager.get_setting("tax_rate"))
            self.invoice_prefix.setText(self.settings_manager.get_setting("invoice_prefix"))
            self.backup_enabled.setChecked(self.settings_manager.get_setting("backup_enabled"))
            self.backup_interval.setValue(self.settings_manager.get_setting("backup_interval_days"))
            self.backup_folder.setText(self.settings_manager.get_setting("backup_folder"))
            self.default_quantity.setValue(self.settings_manager.get_setting("default_product_quantity"))
            self.default_cost.setValue(self.settings_manager.get_setting("default_product_cost"))
            self.default_price.setValue(self.settings_manager.get_setting("default_product_price"))
            self.language_combo.setCurrentText("Español" if self.settings_manager.get_setting("language") == "es" else "English")
            self.autosave_enabled.setChecked(self.settings_manager.get_setting("auto_save_enabled"))
            self.autosave_interval.setValue(self.settings_manager.get_setting("auto_save_interval_minutes"))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión")
        self.setMinimumSize(1200, 800)
        
        # Initialize managers
        self.settings_manager = SettingsManager()
        self.backup_manager = BackupManager(self.settings_manager)
        
        # Connect backup signals
        self.backup_manager.backup_completed.connect(self.show_backup_message)
        self.backup_manager.backup_failed.connect(self.show_backup_error)
        
        # Start backup timer
        self.backup_manager.start_backup_timer()
        
        # Apply initial theme
        self.apply_theme()
        
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
        menu_items = [
            "Inventario", "Añadir producto", "Actualizar producto",
            "Clientes", "Añadir cliente", "Actualizar cliente",
            "Generar Factura", "Administrar Facturas", "Reportes de Ventas", "Historial de Compras"
        ]
        
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
        
        # Settings button at the bottom
        self.settings_btn = QPushButton()
        self.settings_btn.setText("  Settings")
        self.settings_btn.setIcon(QIcon('icons/settings.png'))
        self.settings_btn.setIconSize(QPixmap('icons/settings.png').size())
        self.settings_btn.setCheckable(True)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                font-size: 15px;
                padding: 15px;
                border: none;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
            }
        """)
        self.settings_btn.clicked.connect(lambda: self.open_tab("Settings"))
        menu_layout.addWidget(self.settings_btn)

        # Connect settings changed signal
        self.settings_manager.settings_changed.connect(self.on_settings_changed)

    def apply_theme(self):
        """Apply the current theme settings."""
        theme = self.settings_manager.get_setting("theme")
        font_size = self.settings_manager.get_setting("font_size")
        accent_color = self.settings_manager.get_setting("accent_color")
        
        # Base stylesheet
        if theme == "dark":
            base_style = """
                QWidget {
                    background-color: #2c3e50;
                    color: white;
                }
                QTableWidget {
                    background-color: #34495e;
                    color: white;
                    gridline-color: #2c3e50;
                }
                QTableWidget::item {
                    color: white;
                }
                QTableWidget::item:selected {
                    background-color: #3498db;
                }
                QHeaderView::section {
                    background-color: #2c3e50;
                    color: white;
                }
                QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                    background-color: #34495e;
                    color: white;
                    border: 1px solid #2c3e50;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """
        else:
            base_style = """
                QWidget {
                    background-color: white;
                    color: #2c3e50;
                }
                QTableWidget {
                    background-color: white;
                    color: #2c3e50;
                    gridline-color: #bdc3c7;
                }
                QTableWidget::item {
                    color: #2c3e50;
                }
                QTableWidget::item:selected {
                    background-color: #d0e7fa;
                }
                QHeaderView::section {
                    background-color: #e0e4ea;
                    color: #2c3e50;
                }
                QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                    background-color: white;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """
        
        # Apply font size
        base_style += f"""
            QWidget {{
                font-size: {font_size}px;
            }}
        """
        
        # Apply accent color
        base_style += f"""
            QPushButton:checked {{
                background-color: {accent_color};
            }}
        """
        
        self.setStyleSheet(base_style)

    def on_settings_changed(self):
        """Handle settings changes."""
        self.apply_theme()
        self.backup_manager.start_backup_timer()

    def show_backup_message(self, message):
        """Show backup completion message."""
        QMessageBox.information(self, "Backup", message)

    def show_backup_error(self, error):
        """Show backup error message."""
        QMessageBox.critical(self, "Backup Error", error)

    def open_tab(self, title):
        """Open a new tab or switch to existing one."""
        # Check if tab already exists
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == title:
                self.tab_widget.setCurrentIndex(i)
                return
        
        # Create new tab based on title
        if title == "Inventario":
            new_tab = InventoryTab()
        elif title == "Añadir producto":
            new_tab = AddProductTab()
        elif title == "Actualizar producto":
            new_tab = UpdateProductTab()
        elif title == "Clientes":
            new_tab = ClientsTab()
        elif title == "Añadir cliente":
            new_tab = AddClientTab()
        elif title == "Actualizar cliente":
            new_tab = UpdateClientTab()
        elif title == "Generar Factura":
            new_tab = GenerateInvoiceTab()
        elif title == "Administrar Facturas":
            new_tab = ManageInvoicesTab()
        elif title == "Reportes de Ventas":
            new_tab = SalesReportTab()
        elif title == "Historial de Compras":
            new_tab = PurchaseHistoryTab()
        elif title == "Settings":
            new_tab = SettingsTab()
        else:
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


