from .database import Database

class Category:
    def __init__(self):
        self.db = Database()
    
    # Lấy danh sách tất cả categories
    def getAllCategories(self):
        sql = "SELECT * FROM categories"
        return self.db.fetch_all(sql)
    
    # Lấy category bằng ID
    def getCategoryById(self, category_id):
        sql = "SELECT * FROM categories WHERE category_id = %s"
        return self.db.fetch_one(sql, (category_id,))
    
    # Tạo category mới
    def createCategory(self, category_name):
        sql = "INSERT INTO categories (category_name) VALUES (%s)"
        return self.db.execute(sql, (category_name,))
    
    # Cập nhật category
    def updateCategory(self, category_id, category_name):
        sql = "UPDATE categories SET category_name = %s WHERE category_id = %s"
        return self.db.execute(sql, (category_name, category_id))
    
    # Xóa category
    def deleteCategory(self, category_id):
        sql = "DELETE FROM categories WHERE category_id = %s"
        return self.db.execute(sql, (category_id,))