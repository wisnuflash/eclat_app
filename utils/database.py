from dotenv import load_dotenv
import os

# Import MySQL connector
import mysql.connector
load_dotenv()

HOST = os.getenv("DB_HOST", "localhost")
USER = os.getenv("DB_USER", "root")
PASSWORD = os.getenv("DB_PASSWORD", "")
DATABASE = os.getenv("DB_NAME", "pharmacy_db")
# Fungsi koneksi ke database
def get_db_connection():
    return mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )

# Fungsi untuk mengambil data obat dari database
def fetch_stock_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM stock_obat")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# Fungsi untuk menambah data obat
def add_stock_obat(nama_obat, stok):
    # print(f"DEBUG: Received parameters - nama_obat: {nama_obat}, stok: {stok}")
    conn = get_db_connection()
    cursor = conn.cursor()
    params = (str(nama_obat), int(stok))
    # print(f"DEBUG: Executing query with parameters - {params}")
    try:
        cursor.execute(
            "INSERT INTO stock_obat (nama_obat, stok) VALUES (%s, %s)",
            params
        )
        conn.commit()
    except Exception as err:
        print(f"DEBUG: Error occurred - {err}")
        raise
    finally:
        cursor.close()
        conn.close()

# Fungsi untuk mengupdate data obat
def update_stock_obat(id_obat, nama_obat, stok):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE stock_obat SET nama_obat=%s, stok=%s WHERE id_obat=%s",
        (nama_obat, stok, id_obat)
    )
    conn.commit()
    cursor.close()
    conn.close()

# Fungsi untuk menghapus data obat
def delete_stock_obat(id_obat):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM stock_obat WHERE id_obat=%s",
        (id_obat,)
    )
    conn.commit()
    cursor.close()
    conn.close()