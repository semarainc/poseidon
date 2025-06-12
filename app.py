from flask import Flask, send_from_directory
from datetime import datetime, date, timedelta
from sqlalchemy import func, or_, inspect as sqlalchemy_inspect
import os
import locale

# Import dari paket models
from models.models import db, Barang, Pelanggan, Penjualan, DetailPenjualan, Kategori, Satuan, User, StoreProfile, generate_no_transaksi, init_db_with_app_context

# Import blueprints
from customer.views import customer_blueprint
from products.views import products_blueprint
from sales.views import sales_blueprint
from users.user_views import user_bp
from supplier.views import supplier_blueprint

# Import routes
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.store_routes import store_bp

# Import extensions
from extensions import login_manager, init_extensions

from config import Config

# Konfigurasi Upload Gambar Barang
UPLOAD_FOLDER_NAME = 'images/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def setup_locale(app):
    """Setup locale untuk format tanggal Indonesia"""
    try:
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'Indonesian_Indonesia.1252')
        except locale.Error:
            app.logger.warning("Locale 'id_ID.UTF-8' or 'Indonesian_Indonesia.1252' not found. Using default locale for dates.")

def setup_template_filters(app):
    """Setup custom template filters"""
    @app.template_filter('format_tanggal_indo')
    def format_tanggal_indo_filter(value):
        if isinstance(value, str):
            try:
                value_date = datetime.strptime(value, '%Y-%m-%d').date()
                return value_date.strftime('%d %B %Y')
            except ValueError:
                try:
                    value_dt = datetime.fromisoformat(value)
                    return value_dt.strftime('%d %B %Y')
                except ValueError:
                     return value
        if hasattr(value, 'strftime'):
            return value.strftime('%d %B %Y')
        return value

def setup_context_processors(app):
    """Setup context processors"""
    @app.context_processor
    def inject_store_profile():
        profile = StoreProfile.query.get(1)
        return dict(store_profile=profile)

def setup_misc_routes(app):
    """Additional simple routes like favicon."""
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.static_folder),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')

def initialize_database(app):
    """Membuat semua tabel database jika belum ada dan mengisi data sample jika perlu."""
    with app.app_context():
        inspector = sqlalchemy_inspect(db.engine)
        required_tables = ['barang', 'pelanggan', 'penjualan', 'detail_penjualan', 'user', 'penjualan_antrian', 'store_profile', 'supplier', 'kategori', 'satuan']
        existing_tables = inspector.get_table_names()
        
        tables_exist = all(table_name in existing_tables for table_name in required_tables)

        if not tables_exist:
            app.logger.info("One or more tables not found. Creating all tables...")
            db.create_all()
            app.logger.info("Tables created. Attempting to seed sample data...")
            init_db_with_app_context(app) 
        else:
            app.logger.info("Database tables already exist.")
            if Barang.query.count() == 0 and Pelanggan.query.count() == 0:
                app.logger.info("Main tables (Barang, Pelanggan) are empty. Attempting to seed sample data...")
                init_db_with_app_context(app)

def register_blueprints(app):
    """Register all blueprints"""
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(customer_blueprint)
    app.register_blueprint(products_blueprint)
    app.register_blueprint(sales_blueprint)
    app.register_blueprint(user_bp)
    app.register_blueprint(supplier_blueprint)

def setup_upload_folder(app):
    """Setup upload folder configuration"""
    upload_folder = os.path.join(app.static_folder, UPLOAD_FOLDER_NAME)
    app.config['UPLOAD_FOLDER'] = upload_folder
    
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

def create_app():
    """Application factory for uWSGI / Gunicorn."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Setup upload folder
    setup_upload_folder(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Setup locale
    setup_locale(app)
    
    # Setup template filters
    setup_template_filters(app)
    
    # Setup context processors
    setup_context_processors(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Misc routes (e.g., favicon)
    setup_misc_routes(app)
    
    # Initialize database
    initialize_database(app)
    
    return app

# Create app instance for development
app = create_app()

# WSGI application wrapper for uWSGI compatibility
def application(environ, start_response):
    """WSGI application wrapper"""
    return app(environ, start_response)

if __name__ == '__main__':
    # Create app instance for development
    app.run(debug=True, host='0.0.0.0', port=5000)