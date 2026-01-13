"""
Mock Data Generation Script for Family CFO
===========================================

This script generates comprehensive test data for development and testing purposes.

Usage:
    python scripts/seed_mock_data.py

Features:
    - Creates realistic transactions (6 months of data)
    - Generates accounts with balances
    - Creates insurance policies
    - Adds subscription services
    - Maintains referential integrity
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal, engine
from backend import models
from backend.models import TransactionType, TransactionStatus
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== Configuration ====================

# Transaction categories and merchants
EXPENSE_CATEGORIES = {
    "Groceries": ["Superstore", "Walmart", "Costco", "T&T Supermarket", "Whole Foods"],
    "Dining": ["Tim Hortons", "McDonald's", "Starbucks", "Subway", "Boston Pizza"],
    "Transportation": ["Petro-Canada", "Shell", "Esso", "TransLink", "Uber"],
    "Utilities": ["BC Hydro", "Telus", "Shaw", "FortisBC"],
    "Shopping": ["Amazon", "Best Buy", "Canadian Tire", "Home Depot", "IKEA"],
    "Healthcare": ["Shoppers Drug Mart", "Rexall", "London Drugs"],
    "Entertainment": ["Cineplex", "Netflix", "Spotify", "Steam"],
    "Insurance": ["ICBC", "Manulife", "Sun Life", "TD Insurance"],
}

INCOME_SOURCES = [
    "Salary - Tech Corp",
    "Freelance - Web Development",
    "Investment Dividend",
    "Rental Income",
    "Side Business",
]

# Account types
ACCOUNT_TYPES = {
    "TFSA": {"min": 5000, "max": 80000, "rate": 3.5},
    "RRSP": {"min": 10000, "max": 150000, "rate": 4.0},
    "FHSA": {"min": 0, "max": 40000, "rate": 3.8},
    "Checking": {"min": 500, "max": 5000, "rate": 0.0},
    "Savings": {"min": 2000, "max": 20000, "rate": 2.5},
    "Investment": {"min": 15000, "max": 250000, "rate": 6.5},
}

INSURANCE_TYPES = {
    "Life": ["Manulife", "Sun Life", "Canada Life", "Great-West Life"],
    "Health": ["Blue Cross", "Manulife", "Green Shield", "Sun Life"],
    "Home": ["TD Insurance", "Intact", "Desjardins", "Aviva"],
    "Auto": ["ICBC", "TD Insurance", "Intact", "Belairdirect"],
    "Disability": ["Manulife", "Sun Life", "Great-West Life"],
}

SUBSCRIPTIONS = [
    {"name": "Netflix", "amount": 16.99, "category": "Entertainment"},
    {"name": "Spotify Premium", "amount": 10.99, "category": "Entertainment"},
    {"name": "Amazon Prime", "amount": 99.00, "category": "Shopping", "frequency": "yearly"},
    {"name": "Gym Membership", "amount": 49.99, "category": "Health"},
    {"name": "Cloud Storage", "amount": 9.99, "category": "Technology"},
    {"name": "Meal Kit Service", "amount": 89.99, "category": "Groceries"},
    {"name": "Disney+", "amount": 11.99, "category": "Entertainment"},
    {"name": "New York Times", "amount": 17.00, "category": "News"},
]

# ==================== Helper Functions ====================

def random_date(start_date, end_date):
    """Generate random date between start and end"""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def random_amount(min_amt, max_amt):
    """Generate random amount with 2 decimal places"""
    return round(random.uniform(min_amt, max_amt), 2)

# ==================== Data Generation ====================

def create_users(db):
    """Create test users"""
    print("Creating users...")

    users = [
        {
            "username": "admin",
            "email": "admin@familycfo.com",
            "hashed_password": pwd_context.hash("admin123"),
            "display_name": "Admin User",
            "role": "admin",
            "is_active": True,
        },
        {
            "username": "john",
            "email": "john@example.com",
            "hashed_password": pwd_context.hash("password123"),
            "display_name": "John Smith",
            "role": "user",
            "is_active": True,
        },
        {
            "username": "sarah",
            "email": "sarah@example.com",
            "hashed_password": pwd_context.hash("password123"),
            "display_name": "Sarah Johnson",
            "role": "user",
            "is_active": True,
        },
    ]

    created_users = []
    for user_data in users:
        # Check if user already exists
        existing_user = db.query(models.User).filter(models.User.username == user_data["username"]).first()
        if existing_user:
            print(f"  ⚠️  User '{user_data['username']}' already exists, skipping...")
            created_users.append(existing_user)
        else:
            user = models.User(**user_data)
            db.add(user)
            created_users.append(user)
            print(f"  ✓ Created user: {user_data['username']}")

    db.commit()
    return created_users

def create_transactions(db):
    """Create 6 months of transaction history"""
    print("\nCreating transactions...")

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=180)  # 6 months

    transactions = []

    # Generate expenses
    for _ in range(300):
        category = random.choice(list(EXPENSE_CATEGORIES.keys()))
        merchant = random.choice(EXPENSE_CATEGORIES[category])

        # Different amount ranges based on category
        if category in ["Groceries", "Shopping"]:
            amount = -random_amount(20, 300)
        elif category in ["Utilities", "Insurance"]:
            amount = -random_amount(50, 500)
        elif category == "Dining":
            amount = -random_amount(10, 80)
        elif category == "Transportation":
            amount = -random_amount(30, 150)
        else:
            amount = -random_amount(15, 200)

        transaction = models.Transaction(
            merchant=merchant,
            amount=amount,
            date=random_date(start_date, end_date),
            category=category,
            type=TransactionType.expense,
            status=random.choice([TransactionStatus.posted, TransactionStatus.pending]),
            notes=f"Auto-generated test transaction for {category}",
        )
        transactions.append(transaction)

    # Generate income (monthly)
    for month_offset in range(6):
        income_date = end_date - timedelta(days=30 * month_offset)

        # Primary salary
        transaction = models.Transaction(
            merchant=random.choice(INCOME_SOURCES),
            amount=random_amount(4500, 6500),
            date=income_date,
            category="Income",
            type=TransactionType.income,
            status=TransactionStatus.posted,
            notes="Monthly income",
        )
        transactions.append(transaction)

        # Occasional freelance/side income
        if random.random() < 0.3:  # 30% chance
            transaction = models.Transaction(
                merchant="Freelance - Web Development",
                amount=random_amount(500, 2000),
                date=income_date + timedelta(days=random.randint(1, 28)),
                category="Income",
                type=TransactionType.income,
                status=TransactionStatus.posted,
                notes="Freelance project payment",
            )
            transactions.append(transaction)

    # Add debt payments
    for month_offset in range(6):
        payment_date = end_date - timedelta(days=30 * month_offset + 15)
        transaction = models.Transaction(
            merchant="Credit Card Payment",
            amount=-random_amount(500, 1500),
            date=payment_date,
            category="Debt Payment",
            type=TransactionType.debt_payment,
            status=TransactionStatus.posted,
            notes="Monthly credit card payment",
        )
        transactions.append(transaction)

    db.add_all(transactions)
    db.commit()

    print(f"  ✓ Created {len(transactions)} transactions")
    return transactions

def create_accounts(db):
    """Create various financial accounts"""
    print("\nCreating accounts...")

    accounts = []

    for account_type, config in ACCOUNT_TYPES.items():
        balance = random_amount(config["min"], config["max"])

        # Select institution
        institutions = {
            "TFSA": "TD Bank",
            "RRSP": "Questrade",
            "FHSA": "RBC",
            "Checking": "TD Bank",
            "Savings": "Tangerine",
            "Investment": "Wealthsimple",
        }

        account = models.Account(
            type=account_type,
            balance=balance,
            institution=institutions.get(account_type, "Generic Bank"),
            account_number=f"****{random.randint(1000, 9999)}",
            interest_rate=config["rate"] if config["rate"] > 0 else None,
        )
        accounts.append(account)
        print(f"  ✓ Created {account_type} account: ${balance:,.2f}")

    db.add_all(accounts)
    db.commit()
    return accounts

def create_insurances(db):
    """Create insurance policies"""
    print("\nCreating insurance policies...")

    insurances = []

    for insurance_type, providers in INSURANCE_TYPES.items():
        provider = random.choice(providers)

        # Coverage and premium based on type
        coverage_ranges = {
            "Life": (100000, 1000000, 50, 300),
            "Health": (0, 0, 150, 500),  # No coverage amount for health
            "Home": (200000, 800000, 100, 250),
            "Auto": (50000, 200000, 100, 300),
            "Disability": (0, 0, 80, 200),
        }

        coverage_min, coverage_max, premium_min, premium_max = coverage_ranges[insurance_type]

        insurance = models.Insurance(
            provider=provider,
            type=insurance_type,
            policy_number=f"POL-{random.randint(100000, 999999)}",
            coverage_amount=random_amount(coverage_min, coverage_max) if coverage_max > 0 else None,
            premium=random_amount(premium_min, premium_max),
            premium_frequency=random.choice(["monthly", "yearly"]),
            renewal_date=(datetime.now() + timedelta(days=random.randint(30, 365))).date(),
            beneficiary="Spouse" if insurance_type == "Life" else None,
        )
        insurances.append(insurance)
        print(f"  ✓ Created {insurance_type} insurance: {provider}")

    db.add_all(insurances)
    db.commit()
    return insurances

def create_subscriptions(db):
    """Create subscription services"""
    print("\nCreating subscriptions...")

    subscriptions = []

    for sub_data in SUBSCRIPTIONS:
        frequency = sub_data.get("frequency", "monthly")
        next_due = datetime.now().date() + timedelta(days=random.randint(1, 30))

        subscription = models.Subscription(
            name=sub_data["name"],
            amount=sub_data["amount"],
            frequency=frequency,
            next_due=next_due,
            status="active",
            category=sub_data["category"],
        )
        subscriptions.append(subscription)
        print(f"  ✓ Created subscription: {sub_data['name']} (${sub_data['amount']}/{frequency})")

    db.add_all(subscriptions)
    db.commit()
    return subscriptions

# ==================== Main ====================

def main():
    """Main execution function"""
    print("=" * 60)
    print("Family CFO - Mock Data Generation")
    print("=" * 60)
    print()

    # Create database session
    db = SessionLocal()

    try:
        # Create all data
        users = create_users(db)
        transactions = create_transactions(db)
        accounts = create_accounts(db)
        insurances = create_insurances(db)
        subscriptions = create_subscriptions(db)

        print()
        print("=" * 60)
        print("✅ Mock Data Generation Complete!")
        print("=" * 60)
        print()
        print("Summary:")
        print(f"  - Users: {len(users)}")
        print(f"  - Transactions: {len(transactions)}")
        print(f"  - Accounts: {len(accounts)}")
        print(f"  - Insurance Policies: {len(insurances)}")
        print(f"  - Subscriptions: {len(subscriptions)}")
        print()
        print("Login Credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print()
        print("  Username: john")
        print("  Password: password123")
        print()

    except Exception as e:
        print(f"\n❌ Error generating mock data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
