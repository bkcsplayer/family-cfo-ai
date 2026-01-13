"""
Mock Data Generator for Family CFO
Populates database with realistic test data
"""
import sys
import os
from datetime import datetime, date, timedelta
from random import randint, choice, uniform

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine, Base
import models

# Create tables
Base.metadata.create_all(bind=engine)

def clear_database(db):
    """Clear all data from database"""
    print("🗑️  Clearing existing data...")
    db.query(models.Transaction).delete()
    db.query(models.Asset).delete()
    db.query(models.CanadianAccount).delete()
    db.query(models.Subscription).delete()
    db.query(models.InsurancePolicy).delete()
    db.commit()
    print("✅ Database cleared")

def create_transactions(db):
    """Create realistic transactions for the past 3 months"""
    print("\n💰 Creating transactions...")
    
    merchants = {
        "Food - Groceries": ["Costco", "Walmart", "Loblaws", "Sobeys", "Metro"],
        "Food - Coffee Shops": ["Starbucks", "Tim Hortons", "Second Cup"],
        "Food - Fast Food": ["McDonald's", "Subway", "Burger King"],
        "Food - Restaurants": ["The Keg", "Earls", "Cactus Club"],
        "Transportation - Gas": ["Shell", "Esso", "Petro-Canada"],
        "Transportation - Public Transit": ["Uber", "Lyft", "Transit Pass"],
        "Shopping - Electronics": ["Best Buy", "Apple Store", "Amazon"],
        "Shopping - Clothing": ["Zara", "H&M", "Nike"],
        "Bills - Phone": ["Rogers", "Bell", "Telus"],
        "Entertainment - Streaming Services": ["Netflix", "Spotify", "Disney+"],
        "Housing - Utilities": ["BC Hydro", "Water Bill", "Gas Bill"],
        "Health - Pharmacy": ["Shoppers Drug Mart", "Rexall"],
        "Salary": ["Salary Deposit", "Payroll"]
    }
    
    amounts = {
        "Food - Groceries": (50, 200),
        "Food - Coffee Shops": (5, 15),
        "Food - Fast Food": (10, 25),
        "Food - Restaurants": (40, 120),
        "Transportation - Gas": (50, 80),
        "Transportation - Public Transit": (15, 40),
        "Shopping - Electronics": (100, 1500),
        "Shopping - Clothing": (30, 200),
        "Bills - Phone": (60, 120),
        "Entertainment - Streaming Services": (10, 20),
        "Housing - Utilities": (80, 200),
        "Health - Pharmacy": (20, 60),
        "Salary": (3000, 6000)
    }
    
    transactions = []
    today = date.today()
    
    # Generate transactions for past 90 days
    for days_ago in range(90):
        tx_date = today - timedelta(days=days_ago)
        
        # 2-5 transactions per day
        num_transactions = randint(2, 5)
        
        for _ in range(num_transactions):
            category = choice(list(merchants.keys()))
            merchant = choice(merchants[category])
            min_amt, max_amt = amounts[category]
            amount = round(uniform(min_amt, max_amt), 2)
            
            # Income is positive, expenses are negative
            if category == "Salary":
                # Salary twice a month
                if tx_date.day in [15, 30]:
                    amount = amount
                else:
                    continue
            else:
                amount = -amount
            
            status = choice([models.TransactionStatus.POSTED, models.TransactionStatus.PENDING])
            
            tx = models.Transaction(
                date=tx_date,
                amount=amount,
                merchant=merchant,
                category=category,
                status=status,
                is_amortized=False
            )
            transactions.append(tx)
    
    db.add_all(transactions)
    db.commit()
    print(f"✅ Created {len(transactions)} transactions")

def create_assets(db):
    """Create sample assets"""
    print("\n🏠 Creating assets...")
    
    assets = [
        models.Asset(
            name="Primary Residence",
            type=models.AssetType.REAL_ESTATE,
            value=750000.00,
            equity=250000.00,
            purchase_date=date(2020, 6, 15),
            notes="3-bedroom house in Vancouver"
        ),
        models.Asset(
            name="2018 Honda Civic",
            type=models.AssetType.VEHICLE,
            value=18000.00,
            equity=18000.00,
            purchase_date=date(2018, 3, 10),
            notes="Fully paid off"
        ),
        models.Asset(
            name="Apple Inc. (AAPL)",
            type=models.AssetType.STOCK,
            value=25000.00,
            equity=25000.00,
            purchase_date=date(2021, 1, 5),
            notes="150 shares"
        ),
        models.Asset(
            name="Tesla Inc. (TSLA)",
            type=models.AssetType.STOCK,
            value=15000.00,
            equity=15000.00,
            purchase_date=date(2022, 6, 20),
            notes="50 shares"
        )
    ]
    
    db.add_all(assets)
    db.commit()
    print(f"✅ Created {len(assets)} assets")

def create_canadian_accounts(db):
    """Create Canadian tax-advantaged accounts"""
    print("\n🇨🇦 Creating Canadian accounts...")
    
    accounts = [
        models.CanadianAccount(
            type=models.AccountType.TFSA,
            institution="TD Bank",
            holder="John Doe",
            current_value=45000.00,
            contribution_room=15000.00
        ),
        models.CanadianAccount(
            type=models.AccountType.RRSP,
            institution="RBC",
            holder="John Doe",
            current_value=85000.00,
            contribution_room=25000.00
        ),
        models.CanadianAccount(
            type=models.AccountType.RESP,
            institution="Questrade",
            holder="Jane Doe (Child)",
            current_value=12000.00,
            contribution_room=38000.00
        ),
        models.CanadianAccount(
            type=models.AccountType.FHSA,
            institution="Wealthsimple",
            holder="John Doe",
            current_value=8000.00,
            contribution_room=32000.00
        )
    ]
    
    db.add_all(accounts)
    db.commit()
    print(f"✅ Created {len(accounts)} Canadian accounts")

def create_subscriptions(db):
    """Create recurring subscriptions"""
    print("\n📱 Creating subscriptions...")
    
    today = date.today()
    
    subscriptions = [
        models.Subscription(
            name="Netflix Premium",
            cost=20.99,
            cycle=models.SubscriptionCycle.MONTHLY,
            next_due_date=today + timedelta(days=5),
            merchant_keyword="netflix",
            status="Active"
        ),
        models.Subscription(
            name="Spotify Family",
            cost=16.99,
            cycle=models.SubscriptionCycle.MONTHLY,
            next_due_date=today + timedelta(days=12),
            merchant_keyword="spotify",
            status="Active"
        ),
        models.Subscription(
            name="Amazon Prime",
            cost=99.00,
            cycle=models.SubscriptionCycle.YEARLY,
            next_due_date=today + timedelta(days=180),
            merchant_keyword="amazon prime",
            status="Active"
        ),
        models.Subscription(
            name="Gym Membership",
            cost=45.00,
            cycle=models.SubscriptionCycle.MONTHLY,
            next_due_date=today + timedelta(days=20),
            merchant_keyword="goodlife",
            status="Active"
        )
    ]
    
    db.add_all(subscriptions)
    db.commit()
    print(f"✅ Created {len(subscriptions)} subscriptions")

def create_insurance_policies(db):
    """Create insurance policies"""
    print("\n🛡️  Creating insurance policies...")
    
    today = date.today()
    
    policies = [
        models.InsurancePolicy(
            provider="ICBC",
            type=models.InsuranceType.AUTO,
            policy_number="AUTO-123456",
            renewal_date=today + timedelta(days=90),
            premium=1200.00,
            frequency="Yearly",
            insured_item="2018 Honda Civic"
        ),
        models.InsurancePolicy(
            provider="TD Insurance",
            type=models.InsuranceType.HOME,
            policy_number="HOME-789012",
            renewal_date=today + timedelta(days=120),
            premium=1500.00,
            frequency="Yearly",
            insured_item="Primary Residence"
        ),
        models.InsurancePolicy(
            provider="Manulife",
            type=models.InsuranceType.LIFE,
            policy_number="LIFE-345678",
            renewal_date=today + timedelta(days=200),
            premium=800.00,
            frequency="Yearly",
            insured_item="Term Life $500K"
        )
    ]
    
    db.add_all(policies)
    db.commit()
    print(f"✅ Created {len(policies)} insurance policies")

def print_summary(db):
    """Print database summary"""
    print("\n" + "="*50)
    print("📊 Database Summary")
    print("="*50)
    
    tx_count = db.query(models.Transaction).count()
    asset_count = db.query(models.Asset).count()
    account_count = db.query(models.CanadianAccount).count()
    sub_count = db.query(models.Subscription).count()
    ins_count = db.query(models.InsurancePolicy).count()
    
    print(f"Transactions: {tx_count}")
    print(f"Assets: {asset_count}")
    print(f"Canadian Accounts: {account_count}")
    print(f"Subscriptions: {sub_count}")
    print(f"Insurance Policies: {ins_count}")
    
    # Calculate totals
    total_income = db.query(models.Transaction).filter(
        models.Transaction.amount > 0
    ).with_entities(models.Transaction.amount).all()
    total_income = sum([t[0] for t in total_income])
    
    total_expenses = db.query(models.Transaction).filter(
        models.Transaction.amount < 0
    ).with_entities(models.Transaction.amount).all()
    total_expenses = sum([abs(t[0]) for t in total_expenses])
    
    total_assets = db.query(models.Asset).with_entities(
        models.Asset.value
    ).all()
    total_assets = sum([a[0] for a in total_assets])
    
    print(f"\nTotal Income: ${total_income:,.2f}")
    print(f"Total Expenses: ${total_expenses:,.2f}")
    print(f"Net Savings: ${total_income - total_expenses:,.2f}")
    print(f"Total Asset Value: ${total_assets:,.2f}")
    print("="*50)

def main():
    """Main function"""
    print("\n🚀 Family CFO - Mock Data Generator")
    print("="*50)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        clear_database(db)
        
        # Create mock data
        create_transactions(db)
        create_assets(db)
        create_canadian_accounts(db)
        create_subscriptions(db)
        create_insurance_policies(db)
        
        # Print summary
        print_summary(db)
        
        print("\n✅ Mock data generation complete!")
        print("🎯 Ready for frontend testing\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
