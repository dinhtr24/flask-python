from .database import Database

class Brand:
    def __init__(self):
        self.db = Database()
    
    # Lấy danh sách tất cả brands
    def getAllBrands(self):
        sql = "SELECT * FROM brands"
        return self.db.fetch_all(sql)
    
    # Lấy brand bằng ID
    def getBrandById(self, brand_id):
        sql = "SELECT * FROM brands WHERE brand_id = %s"
        return self.db.fetch_one(sql, (brand_id,))
    
    # Tạo brand mới
    def createBrand(self, brand_name):
        sql = "INSERT INTO brands (brand_name) VALUES (%s)"
        return self.db.execute(sql, (brand_name,))
    
    # Cập nhật brand
    def updateBrand(self, brand_id, brand_name):
        sql = "UPDATE brands SET brand_name = %s WHERE brand_id = %s"
        return self.db.execute(sql, (brand_name, brand_id))
    
    # Xóa brand
    def deleteBrand(self, brand_id):
        sql = "DELETE FROM brands WHERE brand_id = %s"
        return self.db.execute(sql, (brand_id,))