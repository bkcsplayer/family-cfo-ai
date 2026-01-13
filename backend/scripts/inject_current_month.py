"""
Force inject current month (December 2025) transactions
Run this inside Docker container: docker exec familycfo_backend python -c "exec(open('scripts/force_current_month.py').read())"
"""
from datetime import date
from database import SessionLocal
import models

def inject_december_data():
    db = SessionLocal()
    print("🚀 正在强制注入本月 (2025-12) 数据...")

    # 获取当前年份和月份
    today = date.today()
    current_year = today.year
    current_month = today.month 

    new_txs = [
        models.Transaction(
            date=date(current_year, current_month, 5),
            merchant="Costco Holiday",
            amount=-450.00,  # 支出为负数
            category="Groceries",
            status=models.TransactionStatus.POSTED
        ),
        models.Transaction(
            date=date(current_year, current_month, 10),
            merchant="Apple Store",
            amount=-1299.00,
            category="Electronics",
            status=models.TransactionStatus.POSTED
        ),
        models.Transaction(
            date=date(current_year, current_month, 15),
            merchant="Shell Gas",
            amount=-85.50,
            category="Transportation",
            status=models.TransactionStatus.POSTED
        ),
        models.Transaction(
            date=date(current_year, current_month, 20),
            merchant="Salary Deposit",
            amount=5000.00,  # 收入为正数
            category="Income",
            status=models.TransactionStatus.POSTED
        )
    ]

    db.add_all(new_txs)
    db.commit()
    print(f"✅ 成功注入 {len(new_txs)} 笔本月交易！")
    print(f"   - 支出: $1,834.50")
    print(f"   - 收入: $5,000.00")
    db.close()

if __name__ == "__main__":
    inject_december_data()
