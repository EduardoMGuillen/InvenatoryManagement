import sqlite3
from typing import List, Tuple, Optional

class Database:
    def __init__(self, db_name: str = "inventory.db"):
        self.db_name = db_name
        self.create_tables()
        self.add_sample_products_if_empty()
    
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