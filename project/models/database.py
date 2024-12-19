import mysql.connector
from config import Config

class Database:
    def __init__(self):
        # Tạo kết nối với MySQL
        self.connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        # Tạo cursor để thực hiện các câu lệnh SQL
        self.cursor = self.connection.cursor(dictionary=True)

    def close(self):
        # Đóng kết nối khi không sử dụng
        self.cursor.close()
        self.connection.close()

    def execute(self, sql, values=None):
        # Thực thi câu lệnh SQL (INSERT, UPDATE, DELETE)
        self.cursor.execute(sql, values or ())
        self.connection.commit()
        return self.cursor.lastrowid

    def fetch_all(self, sql, values=None):
        # Lấy tất cả kết quả (SELECT)
        self.cursor.execute(sql, values or ())
        return self.cursor.fetchall()

    def fetch_one(self, sql, values=None):
        # Lấy một kết quả (SELECT)
        self.cursor.execute(sql, values or ())
        return self.cursor.fetchone()