from dotenv import load_dotenv
import os

# Import MySQL connector
import mysql.connector
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/eclat_app")
HOST = os.getenv("DB_HOST", "localhost")
USER = os.getenv("DB_USER", "root")
PASSWORD = os.getenv("DB_PASSWORD", "")
DATABASE = os.getenv("DB_NAME", "pharmacy_db")
# Fungsi koneksi ke database
def get_db_connection():
    return mysql.connector.connect(
        host=HOST,
        port=os.getenv("DB_PORT", 3306),
        user=USER,
        password=PASSWORD,
        database=DATABASE

    )


def execute_sql_file(sql_file_path_relative):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(BASE_DIR, sql_file_path_relative)
    try:
        # Buka koneksi ke MySQL
        conn = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            autocommit=True
        )
        cursor = conn.cursor()

        # Baca isi file
        full_path = os.path.abspath(sql_file_path)
        with open(full_path, 'r', encoding='utf-8') as file:
            sql_commands = file.read().split(';')

        # Dapatkan semua tabel di database
        cursor.execute("SHOW TABLES")
        existing_tables = {row[0] for row in cursor.fetchall()}

        for command in sql_commands:
            stmt = command.strip()
            if not stmt:
                continue

            if stmt.lower().startswith("create table"):
                table_name = stmt.split()[2].strip('`').lower()
                if table_name in existing_tables:
                    print(f"ℹ️ Melewati pembuatan tabel '{table_name}' (sudah ada).")
                    continue

            # Eksekusi SQL
            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"❌ Gagal eksekusi:\n{stmt}\n⚠️ Error: {e}")

        print("✅ Setup SQL selesai.")
        return True

    except Exception as e:
        print(f"❌ Koneksi gagal: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

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