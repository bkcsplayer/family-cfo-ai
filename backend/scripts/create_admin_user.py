"""
Create admin user for Family CFO v3.0
"""
import hashlib
from database import SessionLocal
from models import User

def create_admin_user():
    db = SessionLocal()

    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("⚠️  Admin user already exists!")
            print(f"   Username: {existing_admin.username}")
            print(f"   Role: {existing_admin.role}")
            return

        # Create admin user
        password = "admin123"
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        admin_user = User(
            username="admin",
            password_hash=password_hash,
            display_name="Administrator",
            role="Admin",
            status="Active"
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Role: {admin_user.role}")
        print(f"   ID: {admin_user.id}")
        print("\n🔐 Please change the password after first login!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Creating admin user for v3.0...\n")
    create_admin_user()
