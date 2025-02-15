from flask import Flask
import logging
import os
from logging.handlers import RotatingFileHandler
from extensions import db, login_manager
from config import config

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.mkdir('logs')

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'production')  # Default to production
app.config.from_object(config[env])

# Configure logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Import models after db initialization
from models import User, Wing, Quiz, Question, QuizResponse, QuizAnswer, Learning, Notification

@login_manager.user_loader
def load_user(id):
    try:
        return User.query.get(int(id))
    except Exception as e:
        app.logger.error(f"Error loading user: {str(e)}")
        return None

def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create admin user
        admin = User(
            username='purushottam',
            role='admin'
        )
        admin.set_password('Mpkumar98&^')
        db.session.add(admin)
        db.session.commit()
        
        print("Database initialized with admin user!")

# Import routes after everything else
from routes import *

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('app.db') and env == 'development':
            init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
