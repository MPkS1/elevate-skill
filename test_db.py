from flask import Flask
from extensions import db
from models import User
from config import config
import os
import traceback

app = Flask(__name__)
app.config.from_object(config['production'])

# Print the database URL (with password masked)
db_url = app.config['SQLALCHEMY_DATABASE_URI']
masked_url = db_url.replace(db_url.split('@')[0].split(':')[-1], '****')
print(f"Connecting to database: {masked_url}")

db.init_app(app)

def test_connection():
    with app.app_context():
        try:
            # Try to query users
            users = User.query.all()
            print("Successfully connected to database!")
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"- Username: {user.username}, Role: {user.role}")
        except Exception as e:
            print("Error connecting to database:", str(e))
            print("Traceback:")
            print(traceback.format_exc())

if __name__ == "__main__":
    test_connection()
