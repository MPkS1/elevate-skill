from flask import Flask
from extensions import db
from models import User
from config import config
import os

app = Flask(__name__)
app.config.from_object(config['production'])
db.init_app(app)

def update_admin_password():
    with app.app_context():
        admin = User.query.filter_by(username='purushottam').first()
        if admin:
            admin.set_password('Mpkumar98&^')
            db.session.commit()
            print("Admin password updated successfully!")
        else:
            print("Admin user not found!")

if __name__ == "__main__":
    update_admin_password()
