"""
Data Export API - Export transactions and reports in various formats
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date, datetime
import pandas as pd
import io
from calendar import monthrange

from database import get_db
from models import Transaction, Budget, Asset, User
from routers.auth import get_current_user

router = APIRouter(
    prefix="/api/export",
    tags=["export"]
)


@router.get("/transactions/csv")
async def export_transactions_csv(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export transactions to CSV format

    Query Parameters:
    - start_date: Start date (optional, default: beginning of current month)
    - end_date: End date (optional, default: today)
    - category: Filter by category (optional)

    Returns:
    CSV file download
    """
    # Set default date range (current month)
    if not start_date:
        today = date.today()
        start_date = date(today.year, today.month, 1)
    if not end_date:
        end_date = date.today()

    # Query transactions
    query = db.query(Transaction).filter(
        Transaction.date >= start_date,
        Transaction.date <= end_date
    )

    if category:
        query = query.filter(Transaction.category == category)

    transactions = query.order_by(Transaction.date.desc()).all()

    # Convert to DataFrame
    data = []
    for t in transactions:
        data.append({
            "Date": t.date.strftime("%Y-%m-%d"),
            "Merchant": t.merchant,
            "Amount": t.amount,
            "Category": t.category,
            "Status": t.status.value,
            "Notes": t.notes if t.notes else ""
        })

    df = pd.DataFrame(data)

    # Generate CSV
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)

    # Generate filename
    filename = f"transactions_{start_date}_{end_date}.csv"

    print(f"📊 CSV Export: {len(transactions)} transactions ({start_date} to {end_date})")

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/transactions/excel")
async def export_transactions_excel(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export transactions to Excel format with summary sheets

    Query Parameters:
    - start_date: Start date (optional, default: beginning of current month)
    - end_date: End date (optional, default: today)

    Returns:
    Excel file download with multiple sheets:
    - Transactions: All transaction details
    - Summary: Category breakdown
    - Monthly: Month-by-month summary
    """
    # Set default date range (current month)
    if not start_date:
        today = date.today()
        start_date = date(today.year, today.month, 1)
    if not end_date:
        end_date = date.today()

    # Query transactions
    transactions = db.query(Transaction).filter(
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).order_by(Transaction.date.desc()).all()

    # Create Excel writer
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')

    # Sheet 1: All Transactions
    trans_data = []
    for t in transactions:
        trans_data.append({
            "Date": t.date,
            "Merchant": t.merchant,
            "Amount": t.amount,
            "Category": t.category,
            "Status": t.status.value,
            "Notes": t.notes if t.notes else ""
        })
    df_trans = pd.DataFrame(trans_data)
    df_trans.to_excel(writer, sheet_name='Transactions', index=False)

    # Sheet 2: Category Summary
    category_summary = db.query(
        Transaction.category,
        func.count(Transaction.id).label('count'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).group_by(Transaction.category).all()

    summary_data = []
    for cat, count, total in category_summary:
        summary_data.append({
            "Category": cat,
            "Transaction Count": count,
            "Total Amount": total,
            "Average": round(total / count, 2) if count > 0 else 0
        })
    df_summary = pd.DataFrame(summary_data)
    df_summary = df_summary.sort_values('Total Amount')
    df_summary.to_excel(writer, sheet_name='Category Summary', index=False)

    # Sheet 3: Income vs Expenses
    income = sum([t.amount for t in transactions if t.amount > 0])
    expenses = sum([abs(t.amount) for t in transactions if t.amount < 0])
    net = income - expenses

    overview_data = [{
        "Metric": "Total Income",
        "Amount": income
    }, {
        "Metric": "Total Expenses",
        "Amount": expenses
    }, {
        "Metric": "Net Savings",
        "Amount": net
    }, {
        "Metric": "Savings Rate",
        "Amount": f"{(net / income * 100):.1f}%" if income > 0 else "N/A"
    }]
    df_overview = pd.DataFrame(overview_data)
    df_overview.to_excel(writer, sheet_name='Overview', index=False)

    # Save workbook
    writer.close()
    output.seek(0)

    # Generate filename
    filename = f"transactions_{start_date}_{end_date}.xlsx"

    print(f"📊 Excel Export: {len(transactions)} transactions with 3 sheets")

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/budgets/excel")
async def export_budgets_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export all budgets with current status to Excel

    Returns:
    Excel file with budget details and usage statistics
    """
    budgets = db.query(Budget).filter(Budget.is_active == True).all()

    # Prepare data
    budget_data = []
    for budget in budgets:
        # Calculate current spent
        today = date.today()
        first_day = date(today.year, today.month, 1)
        last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])

        total_spent = db.query(func.sum(Transaction.amount)).filter(
            Transaction.category == budget.category,
            Transaction.date >= first_day,
            Transaction.date <= last_day,
            Transaction.amount < 0
        ).scalar()

        current_spent = abs(total_spent) if total_spent else 0.0
        remaining = budget.monthly_limit - current_spent
        percentage_used = (current_spent / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0

        budget_data.append({
            "Category": budget.category,
            "Monthly Limit": budget.monthly_limit,
            "Current Spent": current_spent,
            "Remaining": remaining,
            "Usage %": round(percentage_used, 1),
            "Alert Threshold %": budget.alert_threshold,
            "Status": "Over Budget" if current_spent > budget.monthly_limit else ("Near Limit" if percentage_used >= budget.alert_threshold else "OK")
        })

    df = pd.DataFrame(budget_data)

    # Create Excel file
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    filename = f"budgets_{date.today()}.xlsx"

    print(f"📊 Budget Export: {len(budgets)} budgets")

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/monthly-report/csv")
async def export_monthly_report_csv(
    year: int = Query(..., description="Year (YYYY)"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export monthly financial report to CSV

    Query Parameters:
    - year: Year (required)
    - month: Month 1-12 (required)

    Returns:
    CSV file with monthly summary
    """
    # Calculate date range
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    # Query transactions
    transactions = db.query(Transaction).filter(
        Transaction.date >= first_day,
        Transaction.date <= last_day
    ).all()

    # Calculate metrics
    income_trans = [t for t in transactions if t.amount > 0]
    expense_trans = [t for t in transactions if t.amount < 0]

    total_income = sum([t.amount for t in income_trans])
    total_expenses = abs(sum([t.amount for t in expense_trans]))
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

    # Category breakdown
    category_summary = {}
    for t in expense_trans:
        cat = t.category
        if cat not in category_summary:
            category_summary[cat] = {"count": 0, "total": 0}
        category_summary[cat]["count"] += 1
        category_summary[cat]["total"] += abs(t.amount)

    # Generate report data
    report_data = []

    # Header
    report_data.append({"Section": "Monthly Report", "Value": f"{year}-{month:02d}"})
    report_data.append({"Section": "", "Value": ""})

    # Summary
    report_data.append({"Section": "Total Income", "Value": f"${total_income:.2f}"})
    report_data.append({"Section": "Total Expenses", "Value": f"${total_expenses:.2f}"})
    report_data.append({"Section": "Net Savings", "Value": f"${net_savings:.2f}"})
    report_data.append({"Section": "Savings Rate", "Value": f"{savings_rate:.1f}%"})
    report_data.append({"Section": "", "Value": ""})

    # Category breakdown
    report_data.append({"Section": "Category Breakdown", "Value": ""})
    for cat, data in sorted(category_summary.items(), key=lambda x: x[1]["total"], reverse=True):
        report_data.append({
            "Section": cat,
            "Value": f"${data['total']:.2f} ({data['count']} transactions)"
        })

    df = pd.DataFrame(report_data)

    # Generate CSV
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)

    filename = f"monthly_report_{year}_{month:02d}.csv"

    print(f"📊 Monthly Report Export: {year}-{month:02d}")

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
