import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QTabWidget, QLabel, QTabBar,
                            QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QFormLayout, QSpinBox, QDoubleSpinBox, QStyledItemDelegate)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from login import LoginWindow
from database import Database

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
        menu_items = [
            "Inventario", "Añadir producto", "Actualizar producto",
            "Clientes", "Añadir cliente", "Actualizar cliente",
            "Generar Factura", "Ventas"
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


