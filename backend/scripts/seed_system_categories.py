"""
Script to populate the database with system-defined categories.
These categories will be available to all users and cannot be modified/deleted.

Run: python scripts/seed_system_categories.py
"""
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# System Categories Structure
SYSTEM_CATEGORIES = [
    # ==================== INCOME CATEGORIES ====================
    {
        "name": "Employment Income",
        "type": "income",
        "icon": "💼",
        "color": "#10B981",
        "description": "Income from employment",
        "subcategories": [
            {"name": "Salary", "icon": "💵", "color": "#10B981", "description": "Regular salary/wages"},
            {"name": "Bonus", "icon": "🎁", "color": "#10B981", "description": "Performance bonuses"},
            {"name": "Overtime", "icon": "⏰", "color": "#10B981", "description": "Overtime pay"},
            {"name": "Commission", "icon": "📊", "color": "#10B981", "description": "Sales commissions"},
        ]
    },
    {
        "name": "Investment Income",
        "type": "income",
        "icon": "📈",
        "color": "#059669",
        "description": "Income from investments",
        "subcategories": [
            {"name": "Dividends", "icon": "💰", "color": "#059669", "description": "Stock dividends"},
            {"name": "Interest", "icon": "🏦", "color": "#059669", "description": "Interest income"},
            {"name": "Capital Gains", "icon": "📊", "color": "#059669", "description": "Investment gains"},
            {"name": "TFSA Returns", "icon": "🇨🇦", "color": "#059669", "description": "TFSA investment returns"},
            {"name": "RRSP Returns", "icon": "🇨🇦", "color": "#059669", "description": "RRSP investment returns"},
        ]
    },
    {
        "name": "Government Benefits",
        "type": "income",
        "icon": "🏛️",
        "color": "#34D399",
        "description": "Government assistance and benefits",
        "subcategories": [
            {"name": "CCB (Canada Child Benefit)", "icon": "👶", "color": "#34D399", "description": "Monthly child benefit"},
            {"name": "GST/HST Credit", "icon": "💳", "color": "#34D399", "description": "Tax credit payments"},
            {"name": "OAS (Old Age Security)", "icon": "👴", "color": "#34D399", "description": "Old age pension"},
            {"name": "CPP (Canada Pension)", "icon": "🏦", "color": "#34D399", "description": "Canada Pension Plan"},
        ]
    },
    {
        "name": "Other Income",
        "type": "income",
        "icon": "💸",
        "color": "#6EE7B7",
        "description": "Other income sources",
        "subcategories": [
            {"name": "Rental Income", "icon": "🏠", "color": "#6EE7B7", "description": "Property rental income"},
            {"name": "Business Income", "icon": "🏢", "color": "#6EE7B7", "description": "Self-employment income"},
            {"name": "Freelance Income", "icon": "💻", "color": "#6EE7B7", "description": "Contract/freelance work"},
            {"name": "Insurance Claims", "icon": "🛡️", "color": "#6EE7B7", "description": "Insurance payouts"},
            {"name": "Gifts & Inheritance", "icon": "🎁", "color": "#6EE7B7", "description": "Received gifts/inheritance"},
        ]
    },

    # ==================== EXPENSE CATEGORIES ====================
    {
        "name": "Housing",
        "type": "expense",
        "icon": "🏠",
        "color": "#EF4444",
        "description": "Housing-related expenses",
        "subcategories": [
            {"name": "Rent", "icon": "🏢", "color": "#EF4444", "description": "Monthly rent payments"},
            {"name": "Mortgage Payment", "icon": "🏦", "color": "#EF4444", "description": "Mortgage principal & interest"},
            {"name": "Property Tax", "icon": "🏛️", "color": "#EF4444", "description": "Municipal property taxes"},
            {"name": "Home Insurance", "icon": "🛡️", "color": "#EF4444", "description": "Home insurance premiums"},
            {"name": "HOA/Condo Fees", "icon": "🏘️", "color": "#EF4444", "description": "Homeowner association fees"},
            {"name": "Home Maintenance", "icon": "🔧", "color": "#EF4444", "description": "Repairs and maintenance"},
        ]
    },
    {
        "name": "Utilities",
        "type": "expense",
        "icon": "⚡",
        "color": "#F59E0B",
        "description": "Utility bills",
        "subcategories": [
            {"name": "Electricity", "icon": "💡", "color": "#F59E0B", "description": "Electric bill"},
            {"name": "Water & Sewer", "icon": "💧", "color": "#F59E0B", "description": "Water/sewer charges"},
            {"name": "Natural Gas", "icon": "🔥", "color": "#F59E0B", "description": "Gas heating"},
            {"name": "Internet", "icon": "🌐", "color": "#F59E0B", "description": "Internet service"},
            {"name": "Phone", "icon": "📱", "color": "#F59E0B", "description": "Mobile/landline"},
        ]
    },
    {
        "name": "Transportation",
        "type": "expense",
        "icon": "🚗",
        "color": "#3B82F6",
        "description": "Transportation costs",
        "subcategories": [
            {"name": "Car Loan Payment", "icon": "🏦", "color": "#3B82F6", "description": "Auto loan payments"},
            {"name": "Fuel", "icon": "⛽", "color": "#3B82F6", "description": "Gasoline/diesel"},
            {"name": "Car Insurance", "icon": "🛡️", "color": "#3B82F6", "description": "Auto insurance"},
            {"name": "Car Maintenance", "icon": "🔧", "color": "#3B82F6", "description": "Service & repairs"},
            {"name": "Public Transit", "icon": "🚇", "color": "#3B82F6", "description": "Bus/train/metro"},
            {"name": "Parking", "icon": "🅿️", "color": "#3B82F6", "description": "Parking fees"},
        ]
    },
    {
        "name": "Food & Dining",
        "type": "expense",
        "icon": "🍽️",
        "color": "#EC4899",
        "description": "Food expenses",
        "subcategories": [
            {"name": "Groceries", "icon": "🛒", "color": "#EC4899", "description": "Supermarket shopping"},
            {"name": "Restaurants", "icon": "🍴", "color": "#EC4899", "description": "Dining out"},
            {"name": "Coffee & Snacks", "icon": "☕", "color": "#EC4899", "description": "Quick bites"},
            {"name": "Takeout/Delivery", "icon": "🚚", "color": "#EC4899", "description": "Food delivery"},
        ]
    },
    {
        "name": "Healthcare",
        "type": "expense",
        "icon": "🏥",
        "color": "#14B8A6",
        "description": "Medical expenses",
        "subcategories": [
            {"name": "Health Insurance Premium", "icon": "🛡️", "color": "#14B8A6", "description": "Health insurance"},
            {"name": "Doctor Visits", "icon": "👨‍⚕️", "color": "#14B8A6", "description": "Medical appointments"},
            {"name": "Prescriptions", "icon": "💊", "color": "#14B8A6", "description": "Medications"},
            {"name": "Dental", "icon": "🦷", "color": "#14B8A6", "description": "Dental care"},
            {"name": "Vision", "icon": "👓", "color": "#14B8A6", "description": "Eye care/glasses"},
        ]
    },
    {
        "name": "Insurance",
        "type": "expense",
        "icon": "🛡️",
        "color": "#8B5CF6",
        "description": "Insurance premiums",
        "subcategories": [
            {"name": "Life Insurance", "icon": "👨‍👩‍👧", "color": "#8B5CF6", "description": "Life insurance premium"},
            {"name": "Disability Insurance", "icon": "🤕", "color": "#8B5CF6", "description": "Disability coverage"},
            {"name": "Travel Insurance", "icon": "✈️", "color": "#8B5CF6", "description": "Travel protection"},
        ]
    },
    {
        "name": "Education",
        "type": "expense",
        "icon": "🎓",
        "color": "#6366F1",
        "description": "Education costs",
        "subcategories": [
            {"name": "Tuition", "icon": "🏫", "color": "#6366F1", "description": "School fees"},
            {"name": "Books & Supplies", "icon": "📚", "color": "#6366F1", "description": "Educational materials"},
            {"name": "RESP Contributions", "icon": "🇨🇦", "color": "#6366F1", "description": "Education savings"},
        ]
    },
    {
        "name": "Entertainment",
        "type": "expense",
        "icon": "🎬",
        "color": "#F43F5E",
        "description": "Entertainment & leisure",
        "subcategories": [
            {"name": "Streaming Services", "icon": "📺", "color": "#F43F5E", "description": "Netflix, etc."},
            {"name": "Movies & Events", "icon": "🎟️", "color": "#F43F5E", "description": "Tickets & shows"},
            {"name": "Hobbies", "icon": "🎨", "color": "#F43F5E", "description": "Hobby expenses"},
            {"name": "Gym Membership", "icon": "💪", "color": "#F43F5E", "description": "Fitness memberships"},
        ]
    },
    {
        "name": "Personal Care",
        "type": "expense",
        "icon": "💇",
        "color": "#A855F7",
        "description": "Personal care & grooming",
        "subcategories": [
            {"name": "Haircuts", "icon": "✂️", "color": "#A855F7", "description": "Hair salon"},
            {"name": "Toiletries", "icon": "🧴", "color": "#A855F7", "description": "Personal hygiene products"},
            {"name": "Clothing", "icon": "👔", "color": "#A855F7", "description": "Apparel purchases"},
        ]
    },
    {
        "name": "Taxes",
        "type": "expense",
        "icon": "📋",
        "color": "#DC2626",
        "description": "Tax payments",
        "subcategories": [
            {"name": "Income Tax", "icon": "💼", "color": "#DC2626", "description": "Federal/provincial tax"},
            {"name": "Tax Preparation", "icon": "📊", "color": "#DC2626", "description": "Accounting fees"},
        ]
    },

    # ==================== ASSET CATEGORIES ====================
    {
        "name": "Real Estate",
        "type": "asset",
        "icon": "🏘️",
        "color": "#10B981",
        "description": "Property assets",
        "subcategories": [
            {"name": "Primary Residence", "icon": "🏠", "color": "#10B981", "description": "Main home"},
            {"name": "Investment Property", "icon": "🏢", "color": "#10B981", "description": "Rental properties"},
            {"name": "Vacant Land", "icon": "🌳", "color": "#10B981", "description": "Undeveloped land"},
        ]
    },
    {
        "name": "Vehicles",
        "type": "asset",
        "icon": "🚗",
        "color": "#3B82F6",
        "description": "Vehicle assets",
        "subcategories": [
            {"name": "Car", "icon": "🚙", "color": "#3B82F6", "description": "Automobile"},
            {"name": "Motorcycle", "icon": "🏍️", "color": "#3B82F6", "description": "Motorcycle/scooter"},
            {"name": "RV/Boat", "icon": "🚢", "color": "#3B82F6", "description": "Recreational vehicles"},
        ]
    },
    {
        "name": "Investments",
        "type": "asset",
        "icon": "📊",
        "color": "#8B5CF6",
        "description": "Investment accounts",
        "subcategories": [
            {"name": "Stocks", "icon": "📈", "color": "#8B5CF6", "description": "Stock holdings"},
            {"name": "Bonds", "icon": "📄", "color": "#8B5CF6", "description": "Bond investments"},
            {"name": "Mutual Funds", "icon": "📊", "color": "#8B5CF6", "description": "Fund investments"},
            {"name": "ETFs", "icon": "📉", "color": "#8B5CF6", "description": "Exchange-traded funds"},
            {"name": "Cryptocurrency", "icon": "₿", "color": "#8B5CF6", "description": "Digital currency"},
        ]
    },
    {
        "name": "Registered Accounts (Canada)",
        "type": "asset",
        "icon": "🇨🇦",
        "color": "#EF4444",
        "description": "Canadian registered accounts",
        "subcategories": [
            {"name": "TFSA", "icon": "💰", "color": "#EF4444", "description": "Tax-Free Savings Account"},
            {"name": "RRSP", "icon": "👴", "color": "#EF4444", "description": "Retirement Savings Plan"},
            {"name": "FHSA", "icon": "🏠", "color": "#EF4444", "description": "First Home Savings Account"},
            {"name": "RESP", "icon": "🎓", "color": "#EF4444", "description": "Education Savings Plan"},
        ]
    },
    {
        "name": "Savings & Cash",
        "type": "asset",
        "icon": "💵",
        "color": "#F59E0B",
        "description": "Liquid assets",
        "subcategories": [
            {"name": "Checking Account", "icon": "🏦", "color": "#F59E0B", "description": "Daily banking"},
            {"name": "Savings Account", "icon": "💰", "color": "#F59E0B", "description": "Savings deposits"},
            {"name": "GIC", "icon": "📜", "color": "#F59E0B", "description": "Guaranteed Investment Certificate"},
            {"name": "Cash", "icon": "💵", "color": "#F59E0B", "description": "Physical cash"},
        ]
    },
    {
        "name": "Personal Property",
        "type": "asset",
        "icon": "🎨",
        "color": "#EC4899",
        "description": "Personal belongings",
        "subcategories": [
            {"name": "Jewelry", "icon": "💎", "color": "#EC4899", "description": "Precious jewelry"},
            {"name": "Art & Collectibles", "icon": "🖼️", "color": "#EC4899", "description": "Valuable collections"},
            {"name": "Electronics", "icon": "💻", "color": "#EC4899", "description": "Computers, phones"},
        ]
    },

    # ==================== LIABILITY CATEGORIES ====================
    {
        "name": "Mortgage",
        "type": "liability",
        "icon": "🏠",
        "color": "#EF4444",
        "description": "Home loans",
        "subcategories": [
            {"name": "Primary Mortgage", "icon": "🏠", "color": "#EF4444", "description": "Main home mortgage"},
            {"name": "Home Equity Loan", "icon": "🏦", "color": "#EF4444", "description": "HELOC/home equity line"},
            {"name": "Investment Property Mortgage", "icon": "🏢", "color": "#EF4444", "description": "Rental property loan"},
        ]
    },
    {
        "name": "Auto Loans",
        "type": "liability",
        "icon": "🚗",
        "color": "#F59E0B",
        "description": "Vehicle financing",
        "subcategories": [
            {"name": "Car Loan", "icon": "🚙", "color": "#F59E0B", "description": "Auto financing"},
            {"name": "Car Lease", "icon": "📝", "color": "#F59E0B", "description": "Vehicle lease"},
        ]
    },
    {
        "name": "Credit Cards",
        "type": "liability",
        "icon": "💳",
        "color": "#DC2626",
        "description": "Credit card debt",
        "subcategories": [
            {"name": "Credit Card", "icon": "💳", "color": "#DC2626", "description": "Credit card balance"},
            {"name": "Line of Credit", "icon": "🏦", "color": "#DC2626", "description": "Personal LOC"},
        ]
    },
    {
        "name": "Student Loans",
        "type": "liability",
        "icon": "🎓",
        "color": "#8B5CF6",
        "description": "Education debt",
        "subcategories": [
            {"name": "Federal Student Loan", "icon": "🏛️", "color": "#8B5CF6", "description": "Government student loans"},
            {"name": "Private Student Loan", "icon": "🏦", "color": "#8B5CF6", "description": "Bank student loans"},
        ]
    },
    {
        "name": "Personal Loans",
        "type": "liability",
        "icon": "💰",
        "color": "#6366F1",
        "description": "Personal debt",
        "subcategories": [
            {"name": "Personal Loan", "icon": "🏦", "color": "#6366F1", "description": "Unsecured personal loan"},
            {"name": "Family Loan", "icon": "👨‍👩‍👧", "color": "#6366F1", "description": "Loans from family"},
        ]
    },
    {
        "name": "Other Liabilities",
        "type": "liability",
        "icon": "📋",
        "color": "#64748B",
        "description": "Other debts",
        "subcategories": [
            {"name": "Medical Debt", "icon": "🏥", "color": "#64748B", "description": "Healthcare bills"},
            {"name": "Tax Liability", "icon": "🏛️", "color": "#64748B", "description": "Owed taxes"},
        ]
    },
]

def seed_categories(db: Session):
    """Seed the database with system categories."""
    print("🌱 Starting to seed system categories...")

    # Check if system categories already exist
    existing_count = db.query(models.Category).filter(models.Category.is_system == True).count()
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing system categories.")
        response = input("Do you want to recreate them? This will delete existing system categories (y/n): ")
        if response.lower() != 'y':
            print("❌ Seeding cancelled.")
            return

        # Delete existing system categories
        db.query(models.Category).filter(models.Category.is_system == True).delete()
        db.commit()
        print("🗑️  Deleted existing system categories.")

    total_created = 0

    for category_data in SYSTEM_CATEGORIES:
        # Create parent category
        parent = models.Category(
            name=category_data["name"],
            type=category_data["type"],
            description=category_data.get("description"),
            icon=category_data.get("icon"),
            color=category_data.get("color"),
            is_system=True,
            user_id=None,  # System categories don't belong to any user
            is_active=True
        )
        db.add(parent)
        db.flush()  # Get the ID without committing
        total_created += 1

        # Create subcategories if they exist
        if "subcategories" in category_data:
            for sub_data in category_data["subcategories"]:
                subcategory = models.Category(
                    name=sub_data["name"],
                    type=category_data["type"],  # Inherit parent type
                    parent_id=parent.id,
                    description=sub_data.get("description"),
                    icon=sub_data.get("icon"),
                    color=sub_data.get("color"),
                    is_system=True,
                    user_id=None,
                    is_active=True
                )
                db.add(subcategory)
                total_created += 1

    db.commit()
    print(f"✅ Successfully created {total_created} system categories!")

    # Print summary
    income_count = db.query(models.Category).filter(
        models.Category.type == "income",
        models.Category.is_system == True
    ).count()
    expense_count = db.query(models.Category).filter(
        models.Category.type == "expense",
        models.Category.is_system == True
    ).count()
    asset_count = db.query(models.Category).filter(
        models.Category.type == "asset",
        models.Category.is_system == True
    ).count()
    liability_count = db.query(models.Category).filter(
        models.Category.type == "liability",
        models.Category.is_system == True
    ).count()

    print(f"\n📊 Summary:")
    print(f"   💰 Income categories: {income_count}")
    print(f"   💸 Expense categories: {expense_count}")
    print(f"   📈 Asset categories: {asset_count}")
    print(f"   📉 Liability categories: {liability_count}")
    print(f"   ━━━━━━━━━━━━━━━━━━━━━")
    print(f"   🎯 Total: {total_created}")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_categories(db)
    finally:
        db.close()
