from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os
# Import dotenv to load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/eclat_app")   
class SQLAlchemySetup:
    def __init__(self, db_url=DATABASE_URL):
        """Inisialisasi setup SQLAlchemy dengan URL database"""
        self.db_url = db_url
        self.engine = None
        self.Session = None
    
    def init_database(self):
        """Inisialisasi database dengan SQLAlchemy"""
        try:
            # Buat engine tanpa database terlebih dahulu
            base_url = self.db_url.rsplit('/', 1)[0]
            db_name = self.db_url.rsplit('/', 1)[1]
            
            temp_engine = create_engine(base_url)
            
            # Buat database jika belum ada
            with temp_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
                conn.commit()
            
            # Buat engine untuk database yang sudah ada
            self.engine = create_engine(self.db_url)
            self.Session = sessionmaker(bind=self.engine)
            
            print("✅ SQLAlchemy database setup berhasil")
            return True
            
        except SQLAlchemyError as e:
            print(f"❌ SQLAlchemy Error: {e}")
            return False

    # def execute_sql_file(self, sql_file_path_relative):
    #     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    #     sql_file_path = os.path.join(BASE_DIR, sql_file_path_relative)

    #     """Menjalankan file SQL dengan SQLAlchemy"""
    #     print(f"🔄 Menjalankan file SQL: {sql_file_path}")
    #     try:
    #         with open(sql_file_path, 'r', encoding='utf-8') as file:
    #             sql_content = file.read()
    #             print(f"📄 Membaca file SQL: {sql_content}")
            
    #         with self.engine.connect() as conn:
    #             # Split dan jalankan setiap command
    #             sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
    #             print(f"🔍 Ditemukan {len(sql_commands)} perintah SQL untuk dieksekusi")
    #             for command in sql_commands:
    #                 if command and not command.startswith('--'):
    #                     conn.execute(text(command))
                
    #             conn.commit()
    #             print(f"✅ SQL file '{sql_file_path}' berhasil dijalankan")
    #             return True
                
    #     except Exception as e:
    #         print(f"❌ Error: {e}")
    #         return False
    def execute_sql_file(self, sql_file_path_relative):
        
        """Menjalankan file SQL dengan SQLAlchemy"""
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        sql_file_path = os.path.join(BASE_DIR, sql_file_path_relative)

        print(f"🔄 Menjalankan file SQL: {sql_file_path}")
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()
                print(f"📄 Membaca file SQL (potongan): {sql_content[:100]}...")  # print 100 char pertama

            with self.engine.begin() as conn:
                sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
                print(f"🔍 Ditemukan {len(sql_commands)} perintah SQL untuk dieksekusi")
                for command in sql_commands:
                    if command and not command.startswith('--'):
                        conn.execute(text(command))

            print(f"✅ SQL file '{sql_file_path}' berhasil dijalankan")
            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False
