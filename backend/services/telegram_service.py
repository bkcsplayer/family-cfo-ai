"""
Telegram Service - Send notifications and system status updates
"""
import os
import httpx
from typing import Optional
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class TelegramService:
    """Service for sending Telegram notifications"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.admin_user_id = os.getenv("TELEGRAM_ADMIN_USER_ID")
        self.enabled = os.getenv("TELEGRAM_NOTIFICATIONS_ENABLED", "false").lower() == "true"
        
        if not self.bot_token or not self.admin_user_id:
            print("⚠️  Telegram Service disabled - Missing bot token or admin user ID")
            self.enabled = False
        elif self.enabled:
            print(f"✅ Telegram Service enabled - Bot will send to user {self.admin_user_id}")
    
    async def send_message(
        self,
        message: str,
        parse_mode: str = "HTML",
        disable_notification: bool = False
    ) -> bool:
        """
        Send a message to the admin user
        
        Args:
            message: Message text (supports HTML formatting)
            parse_mode: Message formatting (HTML or Markdown)
            disable_notification: Send silently
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            print(f"📱 [Telegram Disabled] Would send: {message}")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json={
                        "chat_id": self.admin_user_id,
                        "text": message,
                        "parse_mode": parse_mode,
                        "disable_notification": disable_notification
                    }
                )
                
                if response.status_code == 200:
                    print(f"✅ Telegram message sent successfully")
                    return True
                else:
                    print(f"❌ Telegram API error: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {str(e)}")
            return False
    
    async def send_system_status(
        self,
        status: dict,
        alert_level: str = "info"
    ) -> bool:
        """
        Send system status update
        
        Args:
            status: Dictionary with system status info
            alert_level: info, warning, error, critical
            
        Returns:
            True if sent successfully
        """
        # Emoji mapping
        emoji_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }
        
        emoji = emoji_map.get(alert_level, "ℹ️")
        
        # Build message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"{emoji} <b>Family CFO System Status</b>\n"
        message += f"<i>{timestamp}</i>\n\n"
        
        for key, value in status.items():
            # Format key nicely
            formatted_key = key.replace("_", " ").title()
            
            # Add status indicator
            if isinstance(value, bool):
                indicator = "✅" if value else "❌"
                message += f"{indicator} {formatted_key}\n"
            elif isinstance(value, dict):
                message += f"\n<b>{formatted_key}:</b>\n"
                for sub_key, sub_value in value.items():
                    sub_formatted = sub_key.replace("_", " ").title()
                    message += f"  • {sub_formatted}: {sub_value}\n"
            else:
                message += f"• {formatted_key}: {value}\n"
        
        return await self.send_message(message)
    
    async def send_startup_notification(self) -> bool:
        """Send notification when system starts"""
        message = """
🚀 <b>Family CFO Backend Started</b>

The Family CFO backend API has successfully started and is ready to serve requests.

<b>Services:</b>
✅ Database Connected
✅ API Server Running
✅ Authentication Ready
✅ Telegram Notifications Active

<i>System is operational</i>
"""
        return await self.send_message(message.strip())
    
    async def send_error_alert(
        self,
        error_type: str,
        error_message: str,
        details: Optional[dict] = None
    ) -> bool:
        """Send error alert"""
        message = f"""
🚨 <b>System Error Alert</b>

<b>Error Type:</b> {error_type}
<b>Message:</b> {error_message}
"""
        
        if details:
            message += "\n<b>Details:</b>\n"
            for key, value in details.items():
                message += f"• {key}: {value}\n"
        
        message += f"\n<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return await self.send_message(message.strip())
    
    async def send_health_check(
        self,
        database_healthy: bool,
        api_healthy: bool,
        additional_info: Optional[dict] = None
    ) -> bool:
        """Send health check status"""
        overall_status = "✅ Healthy" if (database_healthy and api_healthy) else "⚠️ Issues Detected"
        
        status = {
            "overall_status": overall_status,
            "database": "✅ Connected" if database_healthy else "❌ Disconnected",
            "api": "✅ Running" if api_healthy else "❌ Down",
        }
        
        if additional_info:
            status.update(additional_info)
        
        return await self.send_system_status(
            status,
            alert_level="success" if (database_healthy and api_healthy) else "warning"
        )


# Global Telegram service instance
telegram_service = TelegramService()
