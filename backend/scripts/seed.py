from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from datetime import date, timedelta
import sys

def seed_database():
    """
    Seed the database with initial mock data
    """
    db = SessionLocal()
    
    try:
        print("🌱 Starting database seeding...")
        
        # Check if data already exists
        existing_users = db.query(models.User).count()
        if existing_users > 0:
            print("⚠️  Database already contains data. Skipping seed to prevent duplicates.")
            print(f"   Found {existing_users} existing users.")
            return
        
        # 1. Create Admin User
        print("\n1️⃣  Creating admin user...")
        # For development/demo: using simple hash (will implement proper bcrypt in auth endpoints)
        import hashlib
        password = "password123"
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        admin_user = models.User(
            username="admin",
            password_hash=hashed_password,
            display_name="CFO (You)",
            role=models.UserRole.ADMIN,
            status="Active"
        )
        db.add(admin_user)
        print("   ✅ Admin user created (username: admin, password: password123)")
        print("   ⚠️  Note: Using SHA256 for demo. Implement bcrypt in auth endpoints.")
        
        # 2. Create Canadian Accounts
        print("\n2️⃣  Creating Canadian accounts...")
        accounts = [
            models.CanadianAccount(
                type=models.AccountType.TFSA,
                institution="Questrade",
                holder="Dad",
                current_value=45000,
                contribution_room=50000  # 95k limit - 45k used
            ),
            models.CanadianAccount(
                type=models.AccountType.RRSP,
                institution="TD Direct",
                holder="Mom",
                current_value=142000,
                contribution_room=35000  # 177k limit - 142k used
            ),
            models.CanadianAccount(
                type=models.AccountType.RESP,
                institution="Wealthsimple",
                holder="Kid",
                current_value=12000,
                contribution_room=38000  # 50k limit - 12k used
            ),
        ]
        for account in accounts:
            db.add(account)
        print(f"   ✅ Created {len(accounts)} Canadian accounts (TFSA, RRSP, RESP)")
        
        # 3. Create Assets
        print("\n3️⃣  Creating assets...")
        assets = [
            models.Asset(
                name="Main Residence",
                type=models.AssetType.REAL_ESTATE,
                value=1250000,
                equity=850000,
                purchase_date=date(2018, 6, 15)
            ),
            models.Asset(
                name="2023 Toyota Tundra",
                type=models.AssetType.VEHICLE,
                value=65200,
                equity=65200,
                purchase_date=date(2023, 3, 10)
            ),
            models.Asset(
                name="NVIDIA Stock (100 shares)",
                type=models.AssetType.STOCK,
                value=48500,
                equity=48500,
                purchase_date=date(2022, 1, 5)
            ),
        ]
        for asset in assets:
            db.add(asset)
        print(f"   ✅ Created {len(assets)} assets (house, car, stocks)")
        
        # 4. Create Subscriptions
        print("\n4️⃣  Creating subscriptions...")
        subscriptions = [
            models.Subscription(
                name="Netflix Premium",
                cost=22.99,
                cycle=models.SubscriptionCycle.MONTHLY,
                next_due_date=date.today() + timedelta(days=15),
                merchant_keyword="NETFLIX",
                status="Active"
            ),
            models.Subscription(
                name="Amazon Prime",
                cost=139.00,
                cycle=models.SubscriptionCycle.YEARLY,
                next_due_date=date.today() + timedelta(days=180),
                merchant_keyword="AMAZON",
                status="Active"
            ),
        ]
        for sub in subscriptions:
            db.add(sub)
        print(f"   ✅ Created {len(subscriptions)} subscriptions (Netflix, Amazon Prime)")
        
        # 5. Create Transactions
        print("\n5️⃣  Creating transactions...")
        transactions = [
            models.Transaction(
                date=date.today() - timedelta(days=2),
                amount=156.78,
                merchant="Costco Wholesale",
                category="Groceries",
                status=models.TransactionStatus.POSTED
            ),
            models.Transaction(
                date=date.today() - timedelta(days=1),
                amount=65.40,
                merchant="Shell Gas Station",
                category="Transportation",
                status=models.TransactionStatus.POSTED
            ),
            models.Transaction(
                date=date.today(),
                amount=22.99,
                merchant="NETFLIX.COM *subscription",
                category="Entertainment",
                status=models.TransactionStatus.PENDING,
                linked_subscription_id=1  # Link to Netflix
            ),
            models.Transaction(
                date=date.today() - timedelta(days=5),
                amount=245.00,
                merchant="BC Hydro",
                category="Utilities",
                status=models.TransactionStatus.POSTED
            ),
            models.Transaction(
                date=date.today() - timedelta(days=3),
                amount=89.99,
                merchant="Home Depot",
                category="Home Improvement",
                status=models.TransactionStatus.POSTED
            ),
        ]
        for txn in transactions:
            db.add(txn)
        print(f"   ✅ Created {len(transactions)} transactions")
        
        # Commit all changes
        db.commit()
        
        print("\n" + "="*60)
        print("✅ Database Seeded Successfully!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   • Users: 1 (admin)")
        print(f"   • Canadian Accounts: {len(accounts)}")
        print(f"   • Assets: {len(assets)}")
        print(f"   • Subscriptions: {len(subscriptions)}")
        print(f"   • Transactions: {len(transactions)}")
        print("\n🔐 Login Credentials:")
        print("   Username: admin")
        print("   Password: password123")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    
    # Run seeding
    seed_database()
