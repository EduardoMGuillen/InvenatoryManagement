import sqlite3
from typing import List, Tuple, Optional

class Database:
    def __init__(self, db_name: str = "inventory.db"):
        self.db_name = db_name
        self.create_tables()
        self.add_sample_products_if_empty()
        self.add_sample_clients_if_empty()
    
    def create_tables(self):
        """Create necessary tables if they don't exist."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    serial_number TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    cost REAL NOT NULL,
                    price REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    identity_id TEXT UNIQUE NOT NULL,
                    rtn TEXT UNIQUE,
                    phone TEXT,
                    email TEXT,
                    city TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    client_name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    subtotal REAL NOT NULL,
                    tax REAL NOT NULL,
                    total REAL NOT NULL,
                    file_path TEXT NOT NULL,
                    FOREIGN KEY(client_id) REFERENCES clients(id)
                )
            """)
            conn.commit()
    
    def add_product(self, serial_number: str, name: str, quantity: int, cost: float, price: float) -> bool:
        """Add a new product to the database."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO products (serial_number, name, quantity, cost, price)
                    VALUES (?, ?, ?, ?, ?)
                """, (serial_number, name, quantity, cost, price))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def search_products(self, search_term: str, search_type: str) -> List[Tuple]:
        """Search products based on the search term and type."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            if search_type == "Nombre":
                cursor.execute("""
                    SELECT * FROM products 
                    WHERE name LIKE ?
                    ORDER BY name
                """, (f"%{search_term}%",))
            elif search_type == "Número de Serie":
                cursor.execute("""
                    SELECT * FROM products 
                    WHERE serial_number LIKE ?
                    ORDER BY serial_number
                """, (f"%{search_term}%",))
            elif search_type == "ID":
                try:
                    product_id = int(search_term)
                    cursor.execute("""
                        SELECT * FROM products 
                        WHERE id = ?
                    """, (product_id,))
                except ValueError:
                    return []
            
            return cursor.fetchall()
    
    def get_all_products(self) -> List[Tuple]:
        """Get all products from the database."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products ORDER BY name")
            return cursor.fetchall()
    
    def update_product(self, product_id: int, serial_number: str, name: str, 
                      quantity: int, cost: float, price: float) -> bool:
        """Update an existing product."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE products 
                    SET serial_number = ?, name = ?, quantity = ?, cost = ?, price = ?
                    WHERE id = ?
                """, (serial_number, name, quantity, cost, price, product_id))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product from the database."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def add_sample_products_if_empty(self):
        """Add 20 random construction hardware products if the table is empty."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            if count == 0:
                products = [
                    ("SN1001", "Martillo de Uña", 50, 5.50, 9.99),
                    ("SN1002", "Destornillador Plano", 40, 2.00, 4.50),
                    ("SN1003", "Destornillador de Cruz", 35, 2.20, 4.99),
                    ("SN1004", "Llave Inglesa", 25, 7.00, 12.99),
                    ("SN1005", "Alicate Universal", 30, 4.00, 7.99),
                    ("SN1006", "Cinta Métrica 5m", 60, 1.50, 3.99),
                    ("SN1007", "Nivel de Burbuja", 20, 3.00, 6.50),
                    ("SN1008", "Serrucho", 15, 6.00, 11.99),
                    ("SN1009", "Taladro Percutor", 10, 35.00, 59.99),
                    ("SN1010", "Broca para Concreto 6mm", 100, 0.80, 2.00),
                    ("SN1011", "Caja de Herramientas", 12, 10.00, 19.99),
                    ("SN1012", "Cúter Profesional", 45, 1.20, 2.99),
                    ("SN1013", "Guantes de Trabajo", 80, 0.90, 2.50),
                    ("SN1014", "Casco de Seguridad", 18, 8.00, 15.99),
                    ("SN1015", "Lentes de Protección", 25, 2.50, 5.99),
                    ("SN1016", "Cinta Aislante", 70, 0.60, 1.50),
                    ("SN1017", "Pala de Punta", 14, 9.00, 17.99),
                    ("SN1018", "Carretilla de Obra", 8, 35.00, 69.99),
                    ("SN1019", "Mazo de Goma", 22, 3.50, 7.50),
                    ("SN1020", "Flexómetro 3m", 55, 1.10, 2.49),
                ]
                cursor.executemany(
                    "INSERT INTO products (serial_number, name, quantity, cost, price) VALUES (?, ?, ?, ?, ?)",
                    products
                )
                conn.commit()
    
    def add_client(self, name: str, identity_id: str, rtn: str, phone: str, email: str, city: str) -> bool:
        """Add a new client to the database."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO clients (name, identity_id, rtn, phone, email, city)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, identity_id, rtn, phone, email, city))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def get_all_clients(self) -> List[Tuple]:
        """Get all clients from the database."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients ORDER BY name")
            return cursor.fetchall()

    def search_clients(self, search_term: str, search_type: str) -> List[Tuple]:
        """Search clients based on the search term and type."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            if search_type == "Nombre":
                cursor.execute("""
                    SELECT * FROM clients 
                    WHERE name LIKE ?
                    ORDER BY name
                """, (f"%{search_term}%",))
            elif search_type == "ID":
                cursor.execute("""
                    SELECT * FROM clients 
                    WHERE identity_id LIKE ?
                    ORDER BY identity_id
                """, (f"%{search_term}%",))
            elif search_type == "RTN":
                cursor.execute("""
                    SELECT * FROM clients 
                    WHERE rtn LIKE ?
                    ORDER BY rtn
                """, (f"%{search_term}%",))
            
            return cursor.fetchall()

    def update_client(self, client_id: int, name: str, identity_id: str, 
                     rtn: str, phone: str, email: str, city: str) -> bool:
        """Update an existing client."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE clients 
                    SET name = ?, identity_id = ?, rtn = ?, phone = ?, email = ?, city = ?
                    WHERE id = ?
                """, (name, identity_id, rtn, phone, email, city, client_id))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def delete_client(self, client_id: int) -> bool:
        """Delete a client from the database."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
                conn.commit()
                return True
        except sqlite3.Error:
            return False

    def add_sample_clients_if_empty(self):
        """Add 30 sample clients if the table is empty."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clients")
            count = cursor.fetchone()[0]
            if count == 0:
                clients = [
                    ("Juan Carlos Martínez", "0801-1990-12345", "0801-1990-12345-00001", "9999-1234", "juan.martinez@email.com", "Tegucigalpa"),
                    ("María Elena Rodríguez", "0801-1985-23456", "0801-1985-23456-00002", "9999-2345", "maria.rodriguez@email.com", "San Pedro Sula"),
                    ("Carlos Alberto López", "0801-1995-34567", "0801-1995-34567-00003", "9999-3456", "carlos.lopez@email.com", "Choluteca"),
                    ("Ana Patricia Flores", "0801-1988-45678", "0801-1988-45678-00004", "9999-4567", "ana.flores@email.com", "La Ceiba"),
                    ("Roberto José García", "0801-1992-56789", "0801-1992-56789-00005", "9999-5678", "roberto.garcia@email.com", "Comayagua"),
                    ("Laura Isabel Sánchez", "0801-1993-67890", "0801-1993-67890-00006", "9999-6789", "laura.sanchez@email.com", "Tegucigalpa"),
                    ("Miguel Ángel Torres", "0801-1987-78901", "0801-1987-78901-00007", "9999-7890", "miguel.torres@email.com", "San Pedro Sula"),
                    ("Carmen Rosa Vásquez", "0801-1991-89012", "0801-1991-89012-00008", "9999-8901", "carmen.vasquez@email.com", "Choluteca"),
                    ("José Manuel Ramírez", "0801-1989-90123", "0801-1989-90123-00009", "9999-9012", "jose.ramirez@email.com", "La Ceiba"),
                    ("Patricia Elena Mendoza", "0801-1994-01234", "0801-1994-01234-00010", "9999-0123", "patricia.mendoza@email.com", "Comayagua"),
                    ("Fernando Antonio Castro", "0801-1986-12346", "0801-1986-12346-00011", "9999-1235", "fernando.castro@email.com", "Tegucigalpa"),
                    ("Sandra María Ortiz", "0801-1996-23457", "0801-1996-23457-00012", "9999-2346", "sandra.ortiz@email.com", "San Pedro Sula"),
                    ("Ricardo José Mejía", "0801-1985-34568", "0801-1985-34568-00013", "9999-3457", "ricardo.mejia@email.com", "Choluteca"),
                    ("Diana Carolina Reyes", "0801-1993-45679", "0801-1993-45679-00014", "9999-4568", "diana.reyes@email.com", "La Ceiba"),
                    ("Oscar Eduardo Pineda", "0801-1988-56780", "0801-1988-56780-00015", "9999-5679", "oscar.pineda@email.com", "Comayagua"),
                    ("Mónica Alejandra Cruz", "0801-1995-67891", "0801-1995-67891-00016", "9999-6780", "monica.cruz@email.com", "Tegucigalpa"),
                    ("Luis Enrique Morales", "0801-1987-78902", "0801-1987-78902-00017", "9999-7891", "luis.morales@email.com", "San Pedro Sula"),
                    ("Verónica Isabel Rivas", "0801-1992-89013", "0801-1992-89013-00018", "9999-8902", "veronica.rivas@email.com", "Choluteca"),
                    ("Francisco Javier Soto", "0801-1989-90124", "0801-1989-90124-00019", "9999-9013", "francisco.soto@email.com", "La Ceiba"),
                    ("Gabriela María Zelaya", "0801-1994-01235", "0801-1994-01235-00020", "9999-0124", "gabriela.zelaya@email.com", "Comayagua"),
                    ("Alberto José Núñez", "0801-1986-12347", "0801-1986-12347-00021", "9999-1236", "alberto.nunez@email.com", "Tegucigalpa"),
                    ("Claudia Patricia Maradiaga", "0801-1996-23458", "0801-1996-23458-00022", "9999-2347", "claudia.maradiaga@email.com", "San Pedro Sula"),
                    ("Eduardo Antonio Bonilla", "0801-1985-34569", "0801-1985-34569-00023", "9999-3458", "eduardo.bonilla@email.com", "Choluteca"),
                    ("María Fernanda Cáceres", "0801-1993-45670", "0801-1993-45670-00024", "9999-4569", "maria.caceres@email.com", "La Ceiba"),
                    ("Jorge Luis Espinoza", "0801-1988-56781", "0801-1988-56781-00025", "9999-5670", "jorge.espinoza@email.com", "Comayagua"),
                    ("Silvia Elena Padilla", "0801-1995-67892", "0801-1995-67892-00026", "9999-6781", "silvia.padilla@email.com", "Tegucigalpa"),
                    ("Manuel Antonio Rivera", "0801-1987-78903", "0801-1987-78903-00027", "9999-7892", "manuel.rivera@email.com", "San Pedro Sula"),
                    ("Rosa María Valladares", "0801-1992-89014", "0801-1992-89014-00028", "9999-8903", "rosa.valladares@email.com", "Choluteca"),
                    ("Carlos Roberto Alvarado", "0801-1989-90125", "0801-1989-90125-00029", "9999-9014", "carlos.alvarado@email.com", "La Ceiba"),
                    ("Ana Lucía Matamoros", "0801-1994-01236", "0801-1994-01236-00030", "9999-0125", "ana.matamoros@email.com", "Comayagua")
                ]
                cursor.executemany(
                    "INSERT INTO clients (name, identity_id, rtn, phone, email, city) VALUES (?, ?, ?, ?, ?, ?)",
                    clients
                )
                conn.commit()

    def add_invoice(self, client_id, client_name, date, subtotal, tax, total, file_path):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO invoices (client_id, client_name, date, subtotal, tax, total, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (client_id, client_name, date, subtotal, tax, total, file_path))
            conn.commit()
            return cursor.lastrowid

    def get_all_invoices(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices ORDER BY date DESC")
            return cursor.fetchall()

    def get_invoice_by_id(self, invoice_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
            return cursor.fetchone()

    def search_invoices(self, search_term, search_type):
        """Search invoices based on the search term and type."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            if search_type == "Cliente":
                cursor.execute("SELECT * FROM invoices WHERE client_name LIKE ?", (f"%{search_term}%",))
            else:  # ID Factura
                try:
                    invoice_id = int(search_term)
                    cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
                except ValueError:
                    return []
            return cursor.fetchall()

    def delete_invoice(self, invoice_id):
        """Delete an invoice from the database."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
                conn.commit()
                return True
        except sqlite3.Error:
            return False 