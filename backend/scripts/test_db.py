"""
Simplified data generation using direct database connection
Run this in the same environment as the backend
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import random
    from datetime import date, timedelta
    from database import SessionLocal
    import models
    from passlib.context import CryptContext
    
    print("Modules loaded successfully")
    
    db = SessionLocal()
    print("Database connection established")
    
    # Check existing data
    tx_count = db.query(models.Transaction).count()
    print(f"Current transactions: {tx_count}")
    
    if tx_count < 10:
        print("Generating transactions...")
        
        merchants = [
            ("Costco", "Groceries", 150, 400),
            ("Tim Hortons", "Dining", 5, 15),
            ("Shell", "Transport", 60, 120),
        ]
        
        transactions = []
        today = date.today()
        
        for i in range(30):  # Just 30 days for testing
            current_date = today - timedelta(days=i)
            merch, cat, min_amt, max_amt = random.choice(merchants)
            amount = -round(random.uniform(min_amt, max_amt), 2)
            
            tx = models.Transaction(
                date=current_date,
                merchant=merch,
                amount=amount,
                category=cat,
                status=models.TransactionStatus.POSTED
            )
            transactions.append(tx)
        
        db.add_all(transactions)
        db.commit()
        print(f"Added {len(transactions)} transactions")
    else:
        print(f"Already have {tx_count} transactions")
    
    db.close()
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
