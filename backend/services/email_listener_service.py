"""
IMAP Email Listener Service - Monitor inbox for receipt attachments

Monitors receipts@family.inc inbox for emails with PDF/image attachments,
downloads them, and routes to OCR pipeline for automatic processing.
"""
import os
import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Optional
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import re

load_dotenv()


class EmailListenerService:
    """Service for monitoring IMAP inbox and processing receipt attachments"""
    
    def __init__(self):
        # IMAP Configuration
        self.imap_host = os.getenv("IMAP_HOST", os.getenv("SMTP_HOST"))  # Often same as SMTP
        self.imap_port = int(os.getenv("IMAP_PORT", "993"))  # SSL port
        self.imap_username = os.getenv("IMAP_USERNAME", os.getenv("SMTP_USERNAME"))
        self.imap_password = os.getenv("IMAP_PASSWORD", os.getenv("SMTP_PASSWORD"))
        
        # Listener Configuration
        self.enabled = os.getenv("IMAP_LISTENER_ENABLED", "false").lower() == "true"
        self.inbox_folder = os.getenv("IMAP_INBOX_FOLDER", "INBOX")
        self.processed_folder = os.getenv("IMAP_PROCESSED_FOLDER", "INBOX/Processed")
        self.check_interval = int(os.getenv("IMAP_CHECK_INTERVAL", "300"))  # 5 minutes
        
        # Attachment settings
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.heic'}
        self.upload_dir = "uploads"
        
        # Sender whitelist (optional - for security)
        whitelist_str = os.getenv("IMAP_SENDER_WHITELIST", "")
        self.sender_whitelist = [s.strip() for s in whitelist_str.split(",") if s.strip()]
        
        # Validate configuration
        if not all([self.imap_host, self.imap_username, self.imap_password]):
            print("⚠️  IMAP Listener disabled - Missing IMAP configuration")
            self.enabled = False
        elif self.enabled:
            print(f"✅ IMAP Listener enabled - Monitoring {self.imap_username}")
            print(f"   Check interval: {self.check_interval}s")
            if self.sender_whitelist:
                print(f"   Whitelist: {', '.join(self.sender_whitelist)}")
    
    def connect(self) -> imaplib.IMAP4_SSL:
        """
        Connect to IMAP server with SSL
        
        Returns:
            IMAP4_SSL connection object
        """
        try:
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            mail.login(self.imap_username, self.imap_password)
            print(f"✅ Connected to IMAP server: {self.imap_host}")
            return mail
        except Exception as e:
            print(f"❌ IMAP connection failed: {e}")
            raise
    
    def _decode_header_value(self, value: str) -> str:
        """Decode email header value (handles encoding)"""
        if value is None:
            return ""
        
        decoded_parts = decode_header(value)
        decoded_str = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_str += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_str += str(part)
        
        return decoded_str
    
    def _is_sender_allowed(self, sender: str) -> bool:
        """Check if sender is in whitelist (if whitelist is configured)"""
        if not self.sender_whitelist:
            return True  # No whitelist = allow all
        
        sender_lower = sender.lower()
        return any(allowed.lower() in sender_lower for allowed in self.sender_whitelist)
    
    def _extract_sender_info(self, from_header: str) -> Dict[str, str]:
        """
        Extract sender name and email from From header
        
        Returns:
            {"name": "John Doe", "email": "john@example.com"}
        """
        # Pattern: "Name" <email@example.com> or just email@example.com
        match = re.search(r'([^<]+)?<?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>?', from_header)
        
        if match:
            name = match.group(1).strip().strip('"') if match.group(1) else ""
            email_addr = match.group(2).strip()
            return {"name": name, "email": email_addr}
        
        return {"name": "", "email": from_header}
    
    async def process_email_message(self, msg_data: bytes) -> List[Dict]:
        """
        Process a single email message and extract attachments
        
        Args:
            msg_data: Raw email message data
            
        Returns:
            List of processed attachment info dicts
        """
        email_message = email.message_from_bytes(msg_data)
        
        # Extract metadata
        subject = self._decode_header_value(email_message.get("Subject", ""))
        from_header = self._decode_header_value(email_message.get("From", ""))
        date_header = email_message.get("Date", "")
        
        sender_info = self._extract_sender_info(from_header)
        
        print(f"📧 Processing email from {sender_info['email']}: {subject}")
        
        # Check whitelist
        if not self._is_sender_allowed(sender_info['email']):
            print(f"⚠️  Sender {sender_info['email']} not in whitelist, skipping")
            return []
        
        processed_attachments = []
        
        # Process attachments
        if email_message.is_multipart():
            for part in email_message.walk():
                # Skip non-attachment parts
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                
                filename = part.get_filename()
                if not filename:
                    continue
                
                filename = self._decode_header_value(filename)
                file_ext = os.path.splitext(filename)[1].lower()
                
                # Check if allowed file type
                if file_ext not in self.allowed_extensions:
                    print(f"⚠️  Skipping unsupported file type: {filename}")
                    continue
                
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_filename = f"email_{timestamp}_{filename}"
                file_path = os.path.join(self.upload_dir, safe_filename)
                
                # Save attachment
                try:
                    with open(file_path, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    
                    print(f"✅ Saved attachment: {safe_filename}")
                    
                    # Prepare metadata
                    attachment_info = {
                        "filename": safe_filename,
                        "file_path": file_path,
                        "original_filename": filename,
                        "sender_email": sender_info['email'],
                        "sender_name": sender_info['name'],
                        "subject": subject,
                        "date": date_header
                    }
                    
                    processed_attachments.append(attachment_info)
                    
                except Exception as e:
                    print(f"❌ Failed to save attachment {filename}: {e}")
        
        return processed_attachments
    
    async def process_attachments_with_ocr(self, attachments: List[Dict]):
        """
        Process downloaded attachments with OCR pipeline
        
        Args:
            attachments: List of attachment info dicts
        """
        from services.ocr_service import ocr_service
        from database import SessionLocal
        from models import Transaction, TransactionStatus
        from datetime import date
        import json
        
        if not ocr_service.enabled:
            print("⚠️  OCR service disabled, skipping attachment processing")
            return
        
        db = SessionLocal()
        
        try:
            for attachment in attachments:
                file_path = attachment['file_path']
                
                print(f"🔍 Processing attachment with OCR: {attachment['filename']}")
                
                try:
                    # Process with OCR
                    result = await ocr_service.process_receipt(file_path)
                    
                    confidence = result.get('confidence', 0)
                    
                    if confidence < 50:
                        print(f"⚠️  Low confidence ({confidence}%), skipping auto-creation")
                        continue
                    
                    # Create transaction
                    transaction_date = date.today()
                    if result.get('date'):
                        try:
                            transaction_date = datetime.strptime(result['date'], '%Y-%m-%d').date()
                        except:
                            pass
                    
                    # Determine category
                    final_category = result.get('category', 'Uncategorized')
                    if result.get('ai_category') and result.get('ai_confidence', 0) > 80:
                        final_category = result.get('ai_category')
                    
                    # Prepare notes with email metadata
                    ai_metadata = {
                        "source": "email_attachment",
                        "file": attachment['filename'],
                        "sender_email": attachment['sender_email'],
                        "sender_name": attachment['sender_name'],
                        "email_subject": attachment['subject'],
                        "email_date": attachment['date'],
                        "ocr_confidence": result.get('confidence'),
                        "ai_category": result.get('ai_category'),
                        "ai_confidence": result.get('ai_confidence'),
                        "ai_reasoning": result.get('ai_reasoning')
                    }
                    
                    notes = f"Email Receipt (From: {attachment['sender_email']})\n"
                    notes += f"Subject: {attachment['subject']}\n"
                    notes += f"OCR Confidence: {result.get('confidence')}%\n"
                    if result.get('ai_category'):
                        notes += f"AI Category: {result.get('ai_category')} ({result.get('ai_confidence')}%)\n"
                    notes += f"Metadata: {json.dumps(ai_metadata, indent=2)}"
                    
                    # Create transaction
                    new_transaction = Transaction(
                        date=transaction_date,
                        amount=-abs(result.get('amount', 0)),
                        merchant=result.get('merchant', 'Unknown Merchant'),
                        category=final_category,
                        status=TransactionStatus.PENDING,
                        notes=notes
                    )
                    
                    db.add(new_transaction)
                    db.commit()
                    db.refresh(new_transaction)
                    
                    print(f"✅ Transaction created from email: ID={new_transaction.id}")
                    
                    # Send notification
                    try:
                        from services.telegram_service import telegram_service
                        if telegram_service.enabled:
                            await telegram_service.send_message(
                                f"📧 Email Receipt Processed\n\n"
                                f"From: {attachment['sender_email']}\n"
                                f"Merchant: {result.get('merchant')}\n"
                                f"Amount: ${abs(result.get('amount', 0)):.2f}\n"
                                f"Category: {final_category}\n"
                                f"Confidence: {confidence}%"
                            )
                    except Exception as e:
                        print(f"⚠️  Telegram notification failed: {e}")
                    
                except Exception as e:
                    print(f"❌ Failed to process attachment {attachment['filename']}: {e}")
                    import traceback
                    traceback.print_exc()
        
        finally:
            db.close()
    
    async def check_inbox_once(self):
        """
        Check inbox once for new emails with attachments
        """
        if not self.enabled:
            return
        
        try:
            mail = self.connect()
            
            # Select inbox
            mail.select(self.inbox_folder)
            
            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                print("❌ Failed to search inbox")
                return
            
            email_ids = messages[0].split()
            
            if not email_ids:
                print("📭 No new emails")
                return
            
            print(f"📬 Found {len(email_ids)} new email(s)")
            
            all_attachments = []
            
            for email_id in email_ids:
                # Fetch email
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                
                if status != 'OK':
                    continue
                
                # Process email
                attachments = await self.process_email_message(msg_data[0][1])
                all_attachments.extend(attachments)
                
                # Mark as read
                mail.store(email_id, '+FLAGS', '\\Seen')
            
            # Process all attachments with OCR
            if all_attachments:
                await self.process_attachments_with_ocr(all_attachments)
            
            # Logout
            mail.close()
            mail.logout()
            
        except Exception as e:
            print(f"❌ Inbox check failed: {e}")
            import traceback
            traceback.print_exc()
    
    async def start_listener(self):
        """
        Start continuous IMAP listener (runs in background)
        """
        if not self.enabled:
            print("⚠️  IMAP Listener is disabled")
            return
        
        print(f"🚀 Starting IMAP listener (checking every {self.check_interval}s)")
        
        while True:
            try:
                await self.check_inbox_once()
            except Exception as e:
                print(f"❌ Listener error: {e}")
            
            # Wait before next check
            await asyncio.sleep(self.check_interval)


# Global email listener instance
email_listener = EmailListenerService()
