from flask_login import LoginManager
from models.models import db, User

# Initialize Flask-Login
login_manager = LoginManager()

def init_extensions(app):
    """Initialize Flask extensions"""
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))