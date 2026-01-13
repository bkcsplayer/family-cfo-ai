"""
Database Cleanup Script for Family CFO
=======================================

This script clears all data from the database while preserving the schema.
Useful for transitioning from development/testing to production.

Usage:
    python scripts/clear_data.py [options]

Options:
    --all           Clear all data including users (default)
    --keep-users    Keep user accounts, clear only transactional data
    --confirm       Skip confirmation prompt (use with caution)

Examples:
    python scripts/clear_data.py --all
    python scripts/clear_data.py --keep-users
    python scripts/clear_data.py --all --confirm
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal, engine
from backend import models

# ==================== Cleanup Functions ====================

def clear_transactions(db):
    """Delete all transactions"""
    count = db.query(models.Transaction).count()
    db.query(models.Transaction).delete()
    print(f"  ✓ Deleted {count} transactions")
    return count

def clear_accounts(db):
    """Delete all accounts"""
    count = db.query(models.Account).count()
    db.query(models.Account).delete()
    print(f"  ✓ Deleted {count} accounts")
    return count

def clear_insurances(db):
    """Delete all insurance policies"""
    count = db.query(models.Insurance).count()
    db.query(models.Insurance).delete()
    print(f"  ✓ Deleted {count} insurance policies")
    return count

def clear_subscriptions(db):
    """Delete all subscriptions"""
    count = db.query(models.Subscription).count()
    db.query(models.Subscription).delete()
    print(f"  ✓ Deleted {count} subscriptions")
    return count

def clear_users(db):
    """Delete all users"""
    count = db.query(models.User).count()
    db.query(models.User).delete()
    print(f"  ✓ Deleted {count} users")
    return count

# ==================== Main Functions ====================

def clear_all_data(db):
    """Clear all data from the database"""
    print("\nClearing all data...")
    print("-" * 40)

    total = 0
    total += clear_transactions(db)
    total += clear_accounts(db)
    total += clear_insurances(db)
    total += clear_subscriptions(db)
    total += clear_users(db)

    db.commit()

    print("-" * 40)
    print(f"Total records deleted: {total}")
    return total

def clear_transactional_data(db):
    """Clear only transactional data, keep users"""
    print("\nClearing transactional data (keeping users)...")
    print("-" * 40)

    total = 0
    total += clear_transactions(db)
    total += clear_accounts(db)
    total += clear_insurances(db)
    total += clear_subscriptions(db)

    db.commit()

    print("-" * 40)
    print(f"Total records deleted: {total}")
    print(f"Users preserved: {db.query(models.User).count()}")
    return total

def confirm_action(mode):
    """Ask user for confirmation"""
    print()
    print("=" * 60)
    print("⚠️  WARNING: DATABASE CLEANUP")
    print("=" * 60)
    print()

    if mode == "all":
        print("This will DELETE ALL DATA from the database, including:")
        print("  - All users and authentication")
        print("  - All transactions")
        print("  - All accounts")
        print("  - All insurance policies")
        print("  - All subscriptions")
    else:
        print("This will DELETE TRANSACTIONAL DATA from the database:")
        print("  - All transactions")
        print("  - All accounts")
        print("  - All insurance policies")
        print("  - All subscriptions")
        print()
        print("Users will be PRESERVED.")

    print()
    print("This action CANNOT be undone!")
    print()

    response = input("Are you sure you want to continue? (type 'YES' to confirm): ")

    return response.strip() == "YES"

def show_summary(db):
    """Show current database summary"""
    print()
    print("Current Database Status:")
    print("-" * 40)
    print(f"  Users:        {db.query(models.User).count()}")
    print(f"  Transactions: {db.query(models.Transaction).count()}")
    print(f"  Accounts:     {db.query(models.Account).count()}")
    print(f"  Insurances:   {db.query(models.Insurance).count()}")
    print(f"  Subscriptions:{db.query(models.Subscription).count()}")
    print("-" * 40)

# ==================== Main ====================

def main():
    """Main execution function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Clear data from Family CFO database"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Clear all data including users (default)"
    )
    parser.add_argument(
        "--keep-users",
        action="store_true",
        help="Keep user accounts, clear only transactional data"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt"
    )

    args = parser.parse_args()

    # Determine mode
    if args.keep_users:
        mode = "keep-users"
    else:
        mode = "all"

    # Create database session
    db = SessionLocal()

    try:
        print("=" * 60)
        print("Family CFO - Database Cleanup")
        print("=" * 60)

        # Show current status
        show_summary(db)

        # Ask for confirmation unless --confirm flag is used
        if not args.confirm:
            if not confirm_action(mode):
                print("\n❌ Operation cancelled by user.")
                return

        # Execute cleanup
        print()
        if mode == "all":
            total = clear_all_data(db)
        else:
            total = clear_transactional_data(db)

        # Show final summary
        print()
        print("=" * 60)
        print("✅ Database Cleanup Complete!")
        print("=" * 60)

        show_summary(db)

        print()
        if mode == "all":
            print("💡 Tip: Run 'python scripts/seed_mock_data.py' to generate test data")
        else:
            print("💡 Tip: Your user accounts are still active")

        print()

    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
