from app import app, db
from models import User, Wing
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create wings
        wings = [
            Wing(name='Technology'),
            Wing(name='Marketing'),
            Wing(name='Operations'),
            Wing(name='Finance')
        ]
        for wing in wings:
            db.session.add(wing)
        
        # Commit changes to get wing IDs
        db.session.commit()
        
        # Create wing heads
        for i, wing in enumerate(wings):
            wing_head = User(
                username=f'winghead{i+1}',
                role='wing_head',
                wing_id=wing.id
            )
            wing_head.set_password(f'winghead{i+1}')
            db.session.add(wing_head)
        
        # Create some members
        for wing in wings:
            for i in range(3):  # 3 members per wing
                member = User(
                    username=f'member_{wing.name.lower()}_{i+1}',
                    role='member',
                    wing_id=wing.id
                )
                member.set_password('member123')
                db.session.add(member)
        
        # Commit all changes
        db.session.commit()
        
        print("Database initialized successfully!")
        print("\nLogin credentials:")
        print("Admin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nWing Heads:")
        for i in range(len(wings)):
            print(f"  Username: winghead{i+1}")
            print(f"  Password: winghead{i+1}")
        print("\nMembers:")
        print("  Username format: member_[wing]_[number]")
        print("  Password: member123")
        print("  Example: member_technology_1")

if __name__ == '__main__':
    init_db()
