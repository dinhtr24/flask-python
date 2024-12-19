class Config:
    # Database configuration
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PASSWORD = ""
    DB_NAME = "phonezone"
    
    # Flask configuration
    SECRET_KEY = "2b1674f3c145da107936a6cd64e8abe0"
    
    # Thêm cấu hình cho upload
    UPLOAD_FOLDER = 'static/uploads/products'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}