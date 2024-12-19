from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from config import Config
import mysql.connector
import os
from werkzeug.utils import secure_filename
# Import các models
from models.user import User
from models.category import Category
from models.brand import Brand
from models.product import Product
from models.order import Order

# Khởi tạo Flask app và cấu hình
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

# Khởi tạo các đối tượng model
user_model = User()
category_model = Category()
brand_model = Brand()
product_model = Product()
order_model = Order()

# Thiết lập kết nối database
db = mysql.connector.connect(
    host=Config.DB_HOST,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME
)
cursor = db.cursor(dictionary=True)

# MIDDLEWARE (DECORATORS)
# Decorator kiểm tra quyền admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập!')
            return redirect(url_for('admin_login'))
        if session.get('role') != 1:
            flash('Bạn không có quyền thực hiện thao tác này!')
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator kiểm tra đăng nhập (chỉ xem)
def view_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập!')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ROUTES CHO CLIENT
# Route trang chủ
@app.route('/')
def home():
    products = product_model.getAllProducts()
    page = request.args.get('page', 1, type=int)
    per_page = 8
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    current_products = products[start_index:end_index]
    total_pages = (len(products) + per_page - 1) // per_page
    pages = range(1, total_pages + 1)
    has_next = page < total_pages
    has_prev = page > 1
    import random
    featured_products = random.sample(products, min(4, len(products)))
    return render_template('client/home.html', 
                           products=products,
                           featured_products=featured_products,
                           current_products=current_products,
                           page=page,
                           pages=pages,
                           has_next=has_next,
                           has_prev=has_prev)

# Route đăng nhập client
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user_model.getUserByUsername(username)
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['username'] = user['username']  # Thêm dòng này
            session['fullname'] = user['fullname']
            return redirect(url_for('home'))
        flash('Sai tài khoản hoặc mật khẩu!')
    return render_template('client/login.html')

# Route đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        email = request.form['email']
        telephone = request.form['telephone']
        address = request.form['address']
        
        user_model.createUser(username, password, fullname, email, telephone, address)
        flash('Đăng ký thành công!')
        return redirect(url_for('login'))
    return render_template('client/register.html')  # Sửa đường dẫn template

# Đăng xuất
@app.route('/logout')
def logout():
    if session.get('role') == 1:  # Nếu là admin đang đăng xuất
        session.clear()
        return redirect(url_for('admin_login'))
    # Nếu là user thường
    session.clear()
    return redirect(url_for('login'))

# Route hiển thị tất cả sản phẩm
@app.route('/products')
def products():
    products = product_model.getAllProducts()
    categories = category_model.getAllCategories()
    brands = brand_model.getAllBrands()

    # Phân trang
    page = request.args.get('page', 1, type=int)
    per_page = 8
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    current_products = products[start_index:end_index]
    total_pages = (len(products) + per_page - 1) // per_page
    pages = range(1, total_pages + 1)
    has_next = page < total_pages
    has_prev = page > 1

    return render_template('client/products.html', 
                        products=products,
                        current_products=current_products,
                        page=page,
                        pages=pages,
                        has_next=has_next,
                        has_prev=has_prev,
                        categories=categories,
                        brands=brands,
                        id=None)

# Route chi tiết sản phẩm
@app.route('/product/<int:id>')
def product_detail(id):
    product = product_model.getProductById(id)
    return render_template('client/product_detail.html', product=product)

# Route lọc sản phẩm theo danh mục
@app.route('/category/<int:id>')
def product_by_category(id):
    products = product_model.getProductsByCategory(id)
    categories = category_model.getCategoryById(id)
    brands = brand_model.getAllBrands() # Lấy tất cả thương hiệu

      # Phân trang
    page = request.args.get('page', 1, type=int)
    per_page = 8
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    current_products = products[start_index:end_index]
    total_pages = (len(products) + per_page - 1) // per_page
    pages = range(1, total_pages + 1)
    has_next = page < total_pages
    has_prev = page > 1
   
    return render_template('client/products.html', 
                        products=products,
                        current_products=current_products,
                        page=page,
                        pages=pages,
                        has_next=has_next,
                        has_prev=has_prev,
                        categories=[categories] if categories else [],
                        brands=brands,
                        id=id)

# Route lọc sản phẩm theo thương hiệu
@app.route('/brand/<int:id>')
def product_by_brand(id):
    products = product_model.getProductsByBrand(id)
    brands = brand_model.getBrandById(id)
    categories = category_model.getAllCategories() # Lấy tất cả danh mục
     # Phân trang
    page = request.args.get('page', 1, type=int)
    per_page = 8
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    current_products = products[start_index:end_index]
    total_pages = (len(products) + per_page - 1) // per_page
    pages = range(1, total_pages + 1)
    has_next = page < total_pages
    has_prev = page > 1

    return render_template('client/products.html', 
                        products=products,
                        current_products=current_products,
                        page=page,
                        pages=pages,
                        has_next=has_next,
                        has_prev=has_prev,
                        categories=categories,
                        brands=[brands] if brands else [],
                         id=id)

# Route giỏ hàng
@app.route('/cart')
def cart():
    return render_template('client/cart.html')

# Route xem đơn hàng của user
@app.route('/my-orders')
def my_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    orders = order_model.getOrdersByUser(session['user_id'])
    return render_template('client/my_orders.html', orders=orders)

# Route xem chi tiết đơn hàng
@app.route('/order/<int:id>')
def order_detail(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    order = order_model.getOrderById(id)
    if order['user_id'] != session['user_id']:
        return redirect(url_for('home'))
    details = order_model.getOrderDetails(id)
    return render_template('client/order_detail.html', 
                         order=order,
                         details=details)

# Đăng nhập trang admin
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user_model.getUserByUsername(username)
        
        # Kiểm tra người dùng có phải là admin không
        if user and user['password'] == password:
            if user['role'] == 1:  # Nếu là admin
                session['user_id'] = user['id']
                session['role'] = user['role']
                return redirect(url_for('admin_dashboard'))
            else:  # Nếu là user thường
                flash('Bạn không có quyền truy cập vào trang admin')
                return redirect(url_for('login'))
        flash('Sai tài khoản hoặc mật khẩu!')
    return render_template('admin/login.html')

# Route trang dashboard
@app.route('/admin')
# @admin_required
@view_only
def admin_dashboard():
    # Lấy thống kê
    total_users = len(user_model.getAllUsers())
    total_products = len(product_model.getAllProducts())
    # Lấy thông tin orders
    all_orders = order_model.getAllOrders()
    total_orders = len(all_orders)
    pending_orders = len([o for o in all_orders if o['status'] == 0])
    # Lấy 5 đơn hàng gần nhất
    recent_orders = all_orders[:5]
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_products=total_products,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         recent_orders=recent_orders)

# Routes quản lý sản phẩm
@app.route('/admin/products')
#@admin_required
@view_only
def admin_products():
    products = product_model.getAllProducts()
    categories = category_model.getAllCategories()
    brands = brand_model.getAllBrands()
    return render_template('admin/products/index.html',
                         products=products,
                         categories=categories,
                         brands=brands)

# Hàm kiểm tra phần mở rộng file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# Thêm sản phẩm
@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    if request.method == 'POST':
        # Xử lý file upload
        if 'image' not in request.files:
            flash('Không có file nào được chọn')
            return redirect(request.url) 
        file = request.files['image']
        if file.filename == '':
            flash('Không có file nào được chọn')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Tạo tên file duy nhất để tránh trùng lặp
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            # Lưu file
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Đường dẫn để lưu vào database
            image_url = f'/static/uploads/products/{filename}'
            # Tạo sản phẩm mới với đường dẫn ảnh đã lưu
            product_model.createProduct(
                product_name=request.form['product_name'],
                description=request.form['description'],
                price=request.form['price'],
                image_url=image_url,
                cateid=request.form['cateid'],
                brid=request.form['brid']
            )
            flash('Thêm sản phẩm thành công!')
            return redirect(url_for('admin_products'))
    
    categories = category_model.getAllCategories()
    brands = brand_model.getAllBrands()
    return render_template('admin/products/add.html',
                         categories=categories,
                         brands=brands)

# Sửa thông tin sản phẩm
@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(id):
    if request.method == 'POST':
        # Xử lý file upload
        if 'image' not in request.files:
            flash('Không có file nào được chọn')
            return redirect(request.url) 
        file = request.files['image']
        if file.filename == '':
            flash('Không có file nào được chọn')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Tạo tên file duy nhất để tránh trùng lặp
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            # Lưu file
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Đường dẫn để lưu vào database
            image_url = f'/static/uploads/products/{filename}'
            # Tạo sản phẩm mới với đường dẫn ảnh đã lưu
        product_model.updateProduct(
            product_id=id,
            product_name=request.form['product_name'],
            description=request.form['description'],
            price=request.form['price'],
            image_url=image_url,
            cateid=request.form['cateid'],
            brid=request.form['brid']
        )
        flash('Cập nhật sản phẩm thành công!')
        return redirect(url_for('admin_products'))
    
    product = product_model.getProductById(id)
    categories = category_model.getAllCategories()
    brands = brand_model.getAllBrands()
    return render_template('admin/products/edit.html',
                         product=product,
                         categories=categories,
                         brands=brands)

# Xóa sản phẩm
@app.route('/admin/products/delete/<int:id>')
@admin_required
def admin_delete_product(id):
    product_model.deleteProduct(id)
    flash('Xóa sản phẩm thành công!')
    return redirect(url_for('admin_products'))

# Routes quản lý đơn hàng
@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders = order_model.getAllOrders()
    return render_template('admin/orders/index.html', orders=orders)

@app.route('/admin/orders/<int:id>')
@admin_required
def admin_order_detail(id):
    order = order_model.getOrderById(id)
    details = order_model.getOrderDetails(id)
    return render_template('admin/orders/detail.html',
                         order=order,
                         details=details)

@app.route('/admin/orders/status/<int:id>', methods=['POST'])
@admin_required
def admin_update_order_status(id):
    status = request.form['status']
    order_model.updateOrderStatus(id, status)
    flash('Cập nhật trạng thái đơn hàng thành công!')
    return redirect(url_for('admin_order_detail', id=id))

# Routes quản lý categories
@app.route('/admin/categories')
@admin_required
def admin_categories():
    categories = category_model.getAllCategories()
    return render_template('admin/categories/index.html', categories=categories)

# Thêm danh mục
@app.route('/admin/categories/add', methods=['GET', 'POST'])
@admin_required
def admin_add_category():
    if request.method == 'POST':
        category_name = request.form['category_name']
        category_model.createCategory(category_name)
        flash('Thêm danh mục thành công!')
        return redirect(url_for('admin_categories'))
    return render_template('admin/categories/add.html')

# Sửa danh mục
@app.route('/admin/categories/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_category(id):
    if request.method == 'POST':
        category_name = request.form['category_name']
        category_model.updateCategory(id, category_name)
        flash('Cập nhật danh mục thành công!')
        return redirect(url_for('admin_categories'))
    category = category_model.getCategoryById(id)
    return render_template('admin/categories/edit.html', category=category)

# Xóa danh mục
@app.route('/admin/categories/delete/<int:id>')
@admin_required
def admin_delete_category(id):
    category_model.deleteCategory(id)
    flash('Xóa danh mục thành công!')
    return redirect(url_for('admin_categories'))

# Routes quản lý brands
@app.route('/admin/brands')
@admin_required
def admin_brands():
    brands = brand_model.getAllBrands()
    return render_template('admin/brands/index.html', brands=brands)

# Thêm thương hiệu
@app.route('/admin/brands/add', methods=['GET', 'POST'])
@admin_required
def admin_add_brand():
    if request.method == 'POST':
        brand_name = request.form['brand_name']
        brand_model.createBrand(brand_name)
        flash('Thêm thương hiệu thành công!')
        return redirect(url_for('admin_brands'))
    return render_template('admin/brands/add.html')

# Sửa thương hiệu
@app.route('/admin/brands/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_brand(id):
    if request.method == 'POST':
        brand_name = request.form['brand_name']
        brand_model.updateBrand(id, brand_name)
        flash('Cập nhật thương hiệu thành công!')
        return redirect(url_for('admin_brands'))
    brand = brand_model.getBrandById(id)
    return render_template('admin/brands/edit.html', brand=brand)

# Xóa thương hiệu
@app.route('/admin/brands/delete/<int:id>')
@admin_required
def admin_delete_brand(id):
    brand_model.deleteBrand(id)
    flash('Xóa thương hiệu thành công!')
    return redirect(url_for('admin_brands'))

# Routes quản lý users
@app.route('/admin/users')
@admin_required
def admin_users():
    users = user_model.getAllUsers()
    return render_template('admin/users/index.html', users=users)

# Thêm người dùng
@app.route('/admin/users/add', methods=['GET', 'POST'])
@admin_required
def admin_add_user():
    if request.method == 'POST':
        user_model.createUser(
            username=request.form['username'],
            password=request.form['password'],
            fullname=request.form['fullname'],
            email=request.form['email'],
            telephone=request.form['telephone'],
            address=request.form['address']
        )
        flash('Thêm người dùng thành công!')
        return redirect(url_for('admin_users'))
    return render_template('admin/users/add.html')

# Sửa thông tin người dùng
@app.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(id):
    if request.method == 'POST':
        user_model.updateUser(
            user_id=id,
            fullname=request.form['fullname'],
            email=request.form['email'],
            telephone=request.form['telephone'],
            address=request.form['address']
        )
        flash('Cập nhật người dùng thành công!')
        return redirect(url_for('admin_users'))
    user = user_model.getUserById(id)
    return render_template('admin/users/edit.html', user=user)

# Xóa người dùng 
@app.route('/admin/users/delete/<int:id>')
@admin_required
def admin_delete_user(id):
    # Kiểm tra không cho xóa tài khoản đang đăng nhập
    if id == session['user_id']:
        flash('Không thể xóa tài khoản đang đăng nhập!')
        return redirect(url_for('admin_users'))
    user_model.deleteUser(id)
    flash('Xóa người dùng thành công!')
    return redirect(url_for('admin_users'))

@app.context_processor
def get_data():
    return {
        'categories': category_model.getAllCategories(),
        'brands': brand_model.getAllBrands()
    }

# Khởi chạy ứng dụng
if __name__ == '__main__':
    app.run(debug=True)