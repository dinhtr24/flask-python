from .database import Database

class Order:
    def __init__(self):
        self.db = Database()
    
    # Lấy danh sách tất cả orders
    def getAllOrders(self):
        sql = """
            SELECT o.*, u.fullname 
            FROM orders o
            JOIN users u ON o.user_id = u.id
        """
        return self.db.fetch_all(sql)
    
    # Lấy orders của 1 user
    def getOrdersByUser(self, user_id):
        sql = """
            SELECT o.*, u.fullname 
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.user_id = %s
        """
        return self.db.fetch_all(sql, (user_id,))
    
    # Lấy order bằng ID kèm thông tin user
    def getOrderById(self, order_id):
        sql = """
            SELECT o.*, u.fullname 
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.order_id = %s
        """
        return self.db.fetch_one(sql, (order_id,))
    
    # Lấy chi tiết của 1 order
    def getOrderDetails(self, order_id):
        sql = """
            SELECT od.*, p.product_name, p.image_url
            FROM order_details od
            JOIN products p ON od.product_id = p.product_id
            WHERE od.order_id = %s
        """
        return self.db.fetch_all(sql, (order_id,))
    
    # Tạo order mới (cả order và order_details)
    def createOrder(self, user_id, total_price, items):
        # 1. Tạo order trước
        sql_order = "INSERT INTO orders (user_id, total_price, status) VALUES (%s, %s, 0)"
        order_id = self.db.execute(sql_order, (user_id, total_price))
        
        # 2. Tạo order_details cho từng sản phẩm
        sql_detail = """
            INSERT INTO order_details (order_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """
        for item in items:
            self.db.execute(sql_detail, (
                order_id,
                item['product_id'],
                item['quantity'],
                item['price']
            ))
        
        return order_id
    
    # Cập nhật trạng thái order
    def updateOrderStatus(self, order_id, status):
        sql = "UPDATE orders SET status = %s WHERE order_id = %s"
        return self.db.execute(sql, (status, order_id))
    
    # Xóa order (sẽ xóa cả order_details)
    def deleteOrder(self, order_id):
        # 1. Xóa order_details trước
        sql_details = "DELETE FROM order_details WHERE order_id = %s"
        self.db.execute(sql_details, (order_id,))
        
        # 2. Sau đó xóa order
        sql_order = "DELETE FROM orders WHERE order_id = %s"
        return self.db.execute(sql_order, (order_id,))