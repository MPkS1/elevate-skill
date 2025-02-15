from app import app, db, User

def reset_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("All tables dropped successfully!")
        
        # Create all tables
        db.create_all()
        print("All tables created successfully!")
        
        # Create admin user
        admin = User(
            username='purushottam',
            role='admin'
        )
        admin.set_password('Mpkumar98&^')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")

if __name__ == "__main__":
    reset_db()
