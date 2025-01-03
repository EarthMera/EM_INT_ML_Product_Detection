import os
import logging
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RDS Configuration
RDS_HOST = os.getenv("RDS_HOST")
RDS_PORT = int(os.getenv("RDS_PORT", 5432))
RDS_DB_NAME = os.getenv("RDS_DB_NAME")
RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")

# Connection pool
connection_pool = None

def initialize_connection_pool():
    global connection_pool
    if connection_pool is None:
        try:
            connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=RDS_HOST,
                port=RDS_PORT,
                database=RDS_DB_NAME,
                user=RDS_USER,
                password=RDS_PASSWORD
            )
            logger.info("Connection pool initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

def get_connection():
    if connection_pool is None:
        raise Exception("Connection pool is not initialized.")
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)

def initialize_db():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            videos TEXT,  -- Comma-separated video paths
            status TEXT DEFAULT 'pending'
        )
        """)
        conn.commit()
        logger.info("Database initialized.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def add_product(name: str, description: str) -> int:
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, description) VALUES (%s, %s) RETURNING id", (name, description))
        product_id = cursor.fetchone()[0]
        conn.commit()
        return product_id
    except Exception as e:
        logger.error(f"Error adding product: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def get_products() -> list:
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        logger.error(f"Error retrieving products: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def get_product_by_id(product_id: int) -> dict:
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        row = cursor.fetchone()
        return row
    except Exception as e:
        logger.error(f"Error retrieving product: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def update_product(product_id: int, videos: list = None, status: str = None):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if videos:
            cursor.execute("UPDATE products SET videos = %s WHERE id = %s", (",".join(videos), product_id))
        if status:
            cursor.execute("UPDATE products SET status = %s WHERE id = %s", (status, product_id))
        conn.commit()
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def delete_product(product_id: int):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)
