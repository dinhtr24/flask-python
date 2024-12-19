from .database import Database

class User:
    def __init__(self):
        self.db = Database()
    
    # Lấy danh sách tất cả users
    def getAllUsers(self):
        sql = "SELECT * FROM users"
        return self.db.fetch_all(sql)
    
    # Lấy thông tin user bằng ID
    def getUserById(self, user_id):
        sql = "SELECT * FROM users WHERE id = %s"
        return self.db.fetch_one(sql, (user_id,))
    
    # Lấy thông tin user bằng username
    def getUserByUsername(self, username):
        sql = "SELECT * FROM users WHERE username = %s"
        return self.db.fetch_one(sql, (username,))
    
    # Tạo tài khoản user mới
    def createUser(self, username, password, fullname, email, telephone, address):
        sql = """INSERT INTO users 
                (username, password, fullname, email, telephone, address, role) 
                VALUES (%s, %s, %s, %s, %s, %s, 0)"""
        values = (username, password, fullname, email, telephone, address)
        return self.db.execute(sql, values)

    # Cập nhật thông tin user
    def updateUser(self, user_id, fullname, email, telephone, address):
        sql = """UPDATE users 
                SET fullname = %s, email = %s, telephone = %s, address = %s 
                WHERE id = %s"""
        values = (fullname, email, telephone, address, user_id)
        return self.db.execute(sql, values)

    # Xóa user
    def deleteUser(self, user_id):
        sql = "DELETE FROM users WHERE id = %s"
        return self.db.execute(sql, (user_id,))