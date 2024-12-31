import sqlite3
from typing import List, Dict

DATABASE_PATH = "products.db"

def initialize_db():
    """Initialize the SQLite database and create the products table."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        videos TEXT, -- Comma-separated video paths
        status TEXT DEFAULT 'pending'
    )
    """)
    conn.commit()
    conn.close()

def add_product(name: str, description: str) -> int:
    """Add a new product to the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, description) VALUES (?, ?)", (name, description))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return product_id

def get_products() -> List[Dict]:
    """Retrieve all products."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": row[0], "name": row[1], "description": row[2], "videos": row[3], "status": row[4]}
        for row in rows
    ]

def get_product_by_name(name: str) -> Dict:
    """Retrieve a product by name."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "description": row[2], "videos": row[3], "status": row[4]}
    return None

def update_product(name: str, videos: List[str] = None, status: str = None):
    """Update a product's videos or status."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    if videos:
        cursor.execute("UPDATE products SET videos = ? WHERE name = ?", (",".join(videos), name))
    if status:
        cursor.execute("UPDATE products SET status = ? WHERE name = ?", (status, name))
    conn.commit()
    conn.close()

def delete_product(name: str):
    """Delete a product by name."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE name = ?", (name,))
    conn.commit()
    conn.close()
