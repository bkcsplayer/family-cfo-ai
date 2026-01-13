"""
Email Service - Send email notifications and reports
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    """Service for sending email notifications and reports"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_address = os.getenv("EMAIL_FROM_ADDRESS")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "Family CFO")
        self.enabled = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true"
        
        # Validate configuration
        if not all([self.smtp_host, self.smtp_username, self.smtp_password, self.from_address]):
            print("⚠️  Email Service disabled - Missing SMTP configuration")
            self.enabled = False
        elif self.enabled:
            print(f"✅ Email Service enabled - Sending from {self.from_address}")
    
    def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text fallback (optional)
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            print(f"📧 [Email Disabled] Would send to {to}: {subject}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_address}>"
            msg['To'] = to
            msg['Subject'] = subject
            
            # Add text part
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            # Add HTML part
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {to}: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            return False
    
    def send_weekly_report(self, user_email: str, report_data: dict) -> bool:
        """
        Send weekly financial report
        
        Args:
            user_email: Recipient email
            report_data: Dict with week_start, week_end, total_expenses, etc.
        
        Returns:
            True if sent successfully
        """
        subject = f"Weekly Financial Report - {report_data['week_start']} to {report_data['week_end']}"
        
        html_content = self._generate_weekly_report_html(report_data)
        text_content = self._generate_weekly_report_text(report_data)
        
        return self.send_email(user_email, subject, html_content, text_content)
    
    def send_monthly_report(self, user_email: str, report_data: dict) -> bool:
        """
        Send monthly financial report
        
        Args:
            user_email: Recipient email
            report_data: Dict with month, total_income, total_expenses, etc.
        
        Returns:
            True if sent successfully
        """
        subject = f"Monthly Financial Report - {report_data['month']}"
        
        html_content = self._generate_monthly_report_html(report_data)
        text_content = self._generate_monthly_report_text(report_data)
        
        return self.send_email(user_email, subject, html_content, text_content)
    
    def _generate_weekly_report_html(self, data: dict) -> str:
        """Generate HTML for weekly report"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; }}
        .stat-box {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-label {{ color: #666; font-size: 14px; margin-bottom: 5px; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #667eea; }}
        .expense {{ color: #e74c3c; }}
        .income {{ color: #27ae60; }}
        .category-item {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
        .footer {{ background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Weekly Financial Report</h1>
            <p>{data['week_start']} - {data['week_end']}</p>
        </div>
        
        <div class="content">
            <div class="stat-box">
                <div class="stat-label">Total Expenses</div>
                <div class="stat-value expense">${data.get('total_expenses', 0):.2f}</div>
            </div>
            
            <div class="stat-box">
                <div class="stat-label">Total Income</div>
                <div class="stat-value income">${data.get('total_income', 0):.2f}</div>
            </div>
            
            <div class="stat-box">
                <div class="stat-label">Net Savings</div>
                <div class="stat-value">${data.get('net_savings', 0):.2f}</div>
            </div>
            
            <div class="stat-box">
                <h3>Top Categories</h3>
                {self._format_categories_html(data.get('top_categories', []))}
            </div>
            
            <div class="stat-box">
                <h3>Large Expenses</h3>
                {self._format_transactions_html(data.get('large_expenses', []))}
            </div>
        </div>
        
        <div class="footer">
            <p>Family CFO - Your Financial Management System</p>
            <p style="font-size: 12px; color: #999;">Automated Weekly Report</p>
        </div>
    </div>
</body>
</html>
"""
    
    def _generate_monthly_report_html(self, data: dict) -> str:
        """Generate HTML for monthly report"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; }}
        .stat-box {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-label {{ color: #666; font-size: 14px; margin-bottom: 5px; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #f5576c; }}
        .expense {{ color: #e74c3c; }}
        .income {{ color: #27ae60; }}
        .footer {{ background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Monthly Financial Report</h1>
            <p>{data['month']}</p>
        </div>
        
        <div class="content">
            <div class="stat-box">
                <div class="stat-label">Total Income</div>
                <div class="stat-value income">${data.get('total_income', 0):.2f}</div>
            </div>
            
            <div class="stat-box">
                <div class="stat-label">Total Expenses</div>
                <div class="stat-value expense">${data.get('total_expenses', 0):.2f}</div>
            </div>
            
            <div class="stat-box">
                <div class="stat-label">Net Savings</div>
                <div class="stat-value">${data.get('net_savings', 0):.2f}</div>
            </div>
            
            <div class="stat-box">
                <div class="stat-label">Savings Rate</div>
                <div class="stat-value">{data.get('savings_rate', 0):.1f}%</div>
            </div>
            
            <div class="stat-box">
                <h3>Spending by Category</h3>
                {self._format_categories_html(data.get('categories', []))}
            </div>
        </div>
        
        <div class="footer">
            <p>Family CFO - Your Financial Management System</p>
            <p style="font-size: 12px; color: #999;">Automated Monthly Report</p>
        </div>
    </div>
</body>
</html>
"""
    
    def _format_categories_html(self, categories: List[dict]) -> str:
        """Format categories for HTML"""
        if not categories:
            return "<p>No data available</p>"
        
        html = ""
        for cat in categories:
            html += f"""
            <div class="category-item">
                <strong>{cat['name']}</strong>
                <span style="float: right;">${cat['amount']:.2f}</span>
            </div>
            """
        return html
    
    def _format_transactions_html(self, transactions: List[dict]) -> str:
        """Format transactions for HTML"""
        if not transactions:
            return "<p>No large expenses this period</p>"
        
        html = ""
        for tx in transactions:
            html += f"""
            <div class="category-item">
                <strong>{tx['merchant']}</strong>
                <span style="float: right; color: #e74c3c;">${abs(tx['amount']):.2f}</span>
                <br><small style="color: #999;">{tx['date']}</small>
            </div>
            """
        return html
    
    def _generate_weekly_report_text(self, data: dict) -> str:
        """Generate plain text for weekly report"""
        return f"""
Weekly Financial Report
{data['week_start']} - {data['week_end']}

Total Expenses: ${data.get('total_expenses', 0):.2f}
Total Income: ${data.get('total_income', 0):.2f}
Net Savings: ${data.get('net_savings', 0):.2f}

Top Categories:
{self._format_categories_text(data.get('top_categories', []))}

Large Expenses:
{self._format_transactions_text(data.get('large_expenses', []))}

---
Family CFO - Automated Weekly Report
"""
    
    def _generate_monthly_report_text(self, data: dict) -> str:
        """Generate plain text for monthly report"""
        return f"""
Monthly Financial Report
{data['month']}

Total Income: ${data.get('total_income', 0):.2f}
Total Expenses: ${data.get('total_expenses', 0):.2f}
Net Savings: ${data.get('net_savings', 0):.2f}
Savings Rate: {data.get('savings_rate', 0):.1f}%

Spending by Category:
{self._format_categories_text(data.get('categories', []))}

---
Family CFO - Automated Monthly Report
"""
    
    def _format_categories_text(self, categories: List[dict]) -> str:
        """Format categories for plain text"""
        if not categories:
            return "No data available"
        return "\n".join([f"- {cat['name']}: ${cat['amount']:.2f}" for cat in categories])
    
    def _format_transactions_text(self, transactions: List[dict]) -> str:
        """Format transactions for plain text"""
        if not transactions:
            return "No large expenses this period"
        return "\n".join([f"- {tx['merchant']}: ${abs(tx['amount']):.2f} ({tx['date']})" for tx in transactions])


# Global email service instance
email_service = EmailService()
