"""
Advanced Mock Data Generation Script - Family CFO
Generates realistic Canadian family financial data for the past year
"""
import random
from datetime import date, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Ensure tables exist
models.Base.metadata.create_all(bind=engine)

def generate_data():
    db = SessionLocal()
    print("Starting data injection...")

    try:
        # --- 1. Ensure Admin exists ---
        user = db.query(models.User).filter(models.User.username == "admin").first()
        if not user:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            admin = models.User(
                username="admin",
                hashed_password=pwd_context.hash("password123"),
                role=models.UserRole.ADMIN,
                display_name="Chief Financial Officer",
                status="active"
            )
            db.add(admin)
            db.commit()
            print("Admin user created")
        else:
            print("Admin user already exists")

        # --- 2. Core Assets ---
        existing_assets = db.query(models.Asset).count()
        if existing_assets == 0:
            assets = [
                models.Asset(
                    name="Main Residence (Calgary)", 
                    asset_type=models.AssetType.REAL_ESTATE, 
                    current_value=850000.0,
                    purchase_price=750000.0,
                    purchase_date=date(2021, 6, 15),
                    notes="Primary family home in Calgary"
                ),
                models.Asset(
                    name="2024 Toyota Sienna", 
                    asset_type=models.AssetType.VEHICLE, 
                    current_value=68000.0,
                    purchase_price=72000.0,
                    purchase_date=date(2024, 1, 10),
                    notes="Family minivan"
                ),
                models.Asset(
                    name="NVIDIA Stocks (NVDA)", 
                    asset_type=models.AssetType.STOCK, 
                    current_value=48500.0,
                    purchase_price=25000.0,
                    purchase_date=date(2023, 5, 20),
                    notes="Tech stock investment"
                ),
                models.Asset(
                    name="Bitcoin Cold Wallet", 
                    asset_type=models.AssetType.CRYPTO, 
                    current_value=15000.0,
                    purchase_price=20000.0,
                    purchase_date=date(2022, 11, 1),
                    notes="Cryptocurrency holdings"
                )
            ]
            db.add_all(assets)
            db.commit()
            print("Assets injected: " + str(len(assets)))
        else:
            print("Assets already exist: " + str(existing_assets))

        # --- 3. Canadian Accounts ---
        existing_accounts = db.query(models.CanadianAccount).count()
        if existing_accounts == 0:
            accounts = [
                models.CanadianAccount(
                    account_type=models.AccountType.TFSA,
                    institution="Questrade",
                    holder="Dad",
                    balance=82000.0,
                    contribution_room=13000.0
                ),
                models.CanadianAccount(
                    account_type=models.AccountType.RRSP,
                    institution="TD Direct",
                    holder="Mom",
                    balance=45000.0,
                    contribution_room=75000.0
                ),
                models.CanadianAccount(
                    account_type=models.AccountType.RESP,
                    institution="Wealthsimple",
                    holder="Kid",
                    balance=12500.0,
                    contribution_room=37500.0
                )
            ]
            db.add_all(accounts)
            db.commit()
            print("Accounts injected: " + str(len(accounts)))
        else:
            print("Accounts already exist: " + str(existing_accounts))

        # --- 4. Subscriptions ---
        existing_subs = db.query(models.Subscription).count()
        if existing_subs == 0:
            subs = [
                models.Subscription(
                    name="Netflix Premium", 
                    cost=22.99, 
                    billing_cycle=models.SubscriptionCycle.MONTHLY,
                    merchant_keyword="NETFLIX", 
                    next_billing_date=date.today() + timedelta(days=5),
                    status="active"
                ),
                models.Subscription(
                    name="Rogers Internet", 
                    cost=89.99, 
                    billing_cycle=models.SubscriptionCycle.MONTHLY,
                    merchant_keyword="ROGERS", 
                    next_billing_date=date.today() + timedelta(days=10),
                    status="active"
                ),
                models.Subscription(
                    name="Amazon Prime CA", 
                    cost=12.99, 
                    billing_cycle=models.SubscriptionCycle.MONTHLY,
                    merchant_keyword="AMZN Mktp", 
                    next_billing_date=date.today() + timedelta(days=15),
                    status="active"
                ),
                models.Subscription(
                    name="Enmax Utilities", 
                    cost=350.00, 
                    billing_cycle=models.SubscriptionCycle.MONTHLY,
                    merchant_keyword="ENMAX", 
                    next_billing_date=date.today() + timedelta(days=20),
                    status="active"
                )
            ]
            db.add_all(subs)
            db.commit()
            print("Subscriptions injected: " + str(len(subs)))
        else:
            print("Subscriptions already exist: " + str(existing_subs))

        # --- 5. Generate Transactions for past year ---
        existing_txs = db.query(models.Transaction).count()
        if existing_txs < 10:
            print("Generating 365 days of transactions (300+ records)...")
            
            # Canadian merchants
            merchants = [
                ("Costco Wholesale", "Groceries", 150.0, 400.0),
                ("Real Canadian Superstore", "Groceries", 80.0, 200.0),
                ("Sobeys", "Groceries", 60.0, 150.0),
                ("Tim Hortons", "Dining", 5.0, 15.0),
                ("McDonald's", "Dining", 15.0, 40.0),
                ("Boston Pizza", "Dining", 50.0, 120.0),
                ("Shell Station", "Transport", 60.0, 120.0),
                ("Petro-Canada", "Transport", 50.0, 100.0),
                ("Esso", "Transport", 55.0, 110.0),
                ("Home Depot", "House", 50.0, 300.0),
                ("Canadian Tire", "House", 30.0, 150.0),
                ("Shoppers Drug Mart", "Health", 20.0, 80.0),
                ("Cineplex Odeon", "Entertainment", 30.0, 60.0),
                ("Uber Trip", "Transport", 15.0, 45.0),
                ("Amazon.ca", "Shopping", 25.0, 200.0),
                ("Best Buy", "Electronics", 100.0, 500.0),
                ("Sport Chek", "Shopping", 50.0, 200.0),
                ("Winners", "Shopping", 30.0, 100.0),
            ]

            transactions = []
            today = date.today()
            
            for i in range(365):
                current_date = today - timedelta(days=i)
                
                # 70% chance of transactions each day
                if random.random() < 0.7:
                    # 1-3 transactions per day
                    daily_tx_count = random.randint(1, 3)
                    
                    # Add mortgage on 1st of month
                    if current_date.day == 1:
                        transactions.append(models.Transaction(
                            date=current_date, 
                            merchant="Mortgage Payment", 
                            amount=-2400.00, 
                            category="Housing", 
                            status=models.TransactionStatus.POSTED,
                            notes="Monthly mortgage payment"
                        ))
                    
                    for _ in range(daily_tx_count):
                        merch, cat, min_amt, max_amt = random.choice(merchants)
                        amount = -round(random.uniform(min_amt, max_amt), 2)
                        
                        # Recent 5 days are DRAFT, others are POSTED
                        status = models.TransactionStatus.DRAFT if i < 5 else models.TransactionStatus.POSTED
                        
                        tx = models.Transaction(
                            date=current_date,
                            merchant=merch,
                            amount=amount,
                            category=cat,
                            status=status
                        )
                        transactions.append(tx)
            
            # Add monthly salary
            for month in range(12):
                salary_date = today - timedelta(days=month * 30)
                transactions.append(models.Transaction(
                    date=salary_date,
                    merchant="Payroll Deposit",
                    amount=5500.00,
                    category="Salary",
                    status=models.TransactionStatus.POSTED,
                    notes="Monthly salary"
                ))

            db.add_all(transactions)
            db.commit()
            print("Transactions inserted: " + str(len(transactions)))
        else:
            print("Transactions already exist: " + str(existing_txs))

        print("\nData injection complete!")
        print("\nDatabase Statistics:")
        print("  - Users: " + str(db.query(models.User).count()))
        print("  - Assets: " + str(db.query(models.Asset).count()))
        print("  - Accounts: " + str(db.query(models.CanadianAccount).count()))
        print("  - Subscriptions: " + str(db.query(models.Subscription).count()))
        print("  - Transactions: " + str(db.query(models.Transaction).count()))

    except Exception as e:
        print("Error occurred: " + str(e))
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_data()
