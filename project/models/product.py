from .database import Database

class Product:
    def __init__(self):
        self.db = Database()
    
    # Lấy danh sách tất cả products
    def getAllProducts(self):
        sql = """
            SELECT p.*, c.category_name, b.brand_name 
            FROM products p
            JOIN categories c ON p.cateid = c.category_id
            JOIN brands b ON p.brid = b.brand_id
        """
        return self.db.fetch_all(sql)
    
    # Lấy product bằng ID
    def getProductById(self, product_id):
        sql = """
            SELECT p.*, c.category_name, b.brand_name 
            FROM products p
            JOIN categories c ON p.cateid = c.category_id
            JOIN brands b ON p.brid = b.brand_id
            WHERE p.product_id = %s
        """
        return self.db.fetch_one(sql, (product_id,))
    
    # Lấy products theo category
    def getProductsByCategory(self, category_id):
        sql = """
            SELECT p.*, c.category_name, b.brand_name 
            FROM products p
            JOIN categories c ON p.cateid = c.category_id
            JOIN brands b ON p.brid = b.brand_id
            WHERE p.cateid = %s
        """
        return self.db.fetch_all(sql, (category_id,))
    
    # Lấy products theo brand
    def getProductsByBrand(self, brand_id):
        sql = """
            SELECT p.*, c.category_name, b.brand_name 
            FROM products p
            JOIN categories c ON p.cateid = c.category_id
            JOIN brands b ON p.brid = b.brand_id
            WHERE p.brid = %s
        """
        return self.db.fetch_all(sql, (brand_id,))
    
    # Tạo product mới
    def createProduct(self, product_name, description, price, image_url, cateid, brid):
        sql = """
            INSERT INTO products 
            (product_name, description, price, image_url, cateid, brid) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (product_name, description, price, image_url, cateid, brid)
        return self.db.execute(sql, values)
    
    # Cập nhật product
    def updateProduct(self, product_id, product_name, description, price, image_url, cateid, brid):
        sql = """
            UPDATE products 
            SET product_name = %s, description = %s, price = %s, 
                image_url = %s, cateid = %s, brid = %s
            WHERE product_id = %s
        """
        values = (product_name, description, price, image_url, cateid, brid, product_id)
        return self.db.execute(sql, values)
    
    # Xóa product
    def deleteProduct(self, product_id):
        sql = "DELETE FROM products WHERE product_id = %s"
        return self.db.execute(sql, (product_id,))