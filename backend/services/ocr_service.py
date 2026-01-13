"""
OCR Service - Receipt Analysis using OpenRouter Vision API

Extracts transaction data from receipt images:
- Merchant name
- Total amount
- Transaction date
- Line items (optional)
"""
import os
import base64
import json
from typing import Optional, Dict, List
from openai import AsyncOpenAI


class OCRService:
    """Service for analyzing receipt images using Vision AI"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            self.client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                default_headers={
                    "HTTP-Referer": "http://localhost:6501",
                    "X-Title": "Family CFO"
                }
            )
            print("✅ OCR Service initialized with OpenRouter")
        else:
            print("⚠️  OCR Service disabled - OPENROUTER_API_KEY not set")
    
    async def analyze_receipt(self, image_path: str) -> Dict:
        """
        Analyze receipt image and extract transaction details.
        
        Args:
            image_path: Path to the receipt image file
            
        Returns:
            {
                "merchant": "Costco",
                "amount": 234.56,
                "date": "2025-12-28",
                "line_items": [...],
                "confidence": 95
            }
        """
        if not self.enabled:
            raise Exception("OCR service not configured. Set OPENROUTER_API_KEY in .env")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Determine image MIME type
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.heic': 'image/heic',
            '.pdf': 'application/pdf'
        }.get(ext, 'image/jpeg')
        
        prompt = """
Analyze this receipt image and extract the following information:

1. **Merchant Name**: The store/business name (e.g., "Costco", "Walmart", "Shell")
2. **Total Amount**: The final total amount paid (as a positive number)
3. **Date**: Transaction date in YYYY-MM-DD format
4. **Category**: Suggest ONE category from this list:
   - Groceries, Dining, Transport, Utilities, Housing, Shopping, Entertainment, Health, Bills, Other
5. **Line Items** (optional): List of purchased items with their prices

Return ONLY a valid JSON object with this exact structure:
{
    "merchant": "Store Name",
    "amount": 123.45,
    "date": "2025-12-28",
    "category": "Groceries",
    "line_items": [
        {"item": "Product Name", "price": 12.34}
    ],
    "confidence": 95
}

Important Rules:
- Amount should be a positive number (we'll convert to negative later)
- Date MUST be in YYYY-MM-DD format
- Category MUST be one from the list above
- If you cannot find a field, use null (not "Unknown" or empty string)
- Confidence: 0-100 based on image quality and clarity (consider image quality, text legibility, and data completeness)
- Return ONLY the JSON, no markdown formatting or explanations
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}"
                            }
                        }
                    ]
                }],
                max_tokens=1000,
                temperature=0.1  # Low temperature for consistent, accurate extraction
            )
            
            # Parse JSON from response
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            # Validate required fields
            if not isinstance(result.get('merchant'), str):
                result['merchant'] = None
            if not isinstance(result.get('amount'), (int, float)):
                result['amount'] = None
            if not isinstance(result.get('date'), str):
                result['date'] = None
            if not isinstance(result.get('confidence'), (int, float)):
                result['confidence'] = 50  # Default confidence
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON from OCR response: {e}")
            print(f"Raw response: {content}")
            raise Exception(f"Invalid JSON response from OCR: {e}")
        except Exception as e:
            print(f"❌ OCR analysis failed: {e}")
            raise
    
    async def process_receipt(self, image_path: str) -> Dict:
        """
        Complete receipt processing pipeline: OCR + AI Categorization
        
        Args:
            image_path: Path to the receipt image file
            
        Returns:
            {
                "merchant": "Costco",
                "amount": 234.56,
                "date": "2025-12-28",
                "category": "Groceries",
                "confidence": 95,
                "ai_category": "Food - Groceries",  # From AI service
                "ai_confidence": 98
            }
        """
        # Step 1: Extract data from image
        ocr_result = await self.analyze_receipt(image_path)
        
        # Step 2: Enhance with AI categorization if confidence is high enough
        if ocr_result.get('confidence', 0) > 60 and ocr_result.get('merchant'):
            try:
                from services.ai_service import ai_service
                
                if ai_service.enabled:
                    category_result = await ai_service.categorize_transaction(
                        merchant=ocr_result['merchant'],
                        amount=-abs(ocr_result.get('amount', 0)),  # Negative for expense
                        date=ocr_result.get('date')
                    )
                    
                    # Add AI categorization to result
                    ocr_result['ai_category'] = category_result.get('category')
                    ocr_result['ai_confidence'] = category_result.get('confidence')
                    ocr_result['ai_reasoning'] = category_result.get('reasoning')
                    
                    # Use AI category if OCR didn't provide one or AI has higher confidence
                    if not ocr_result.get('category') or category_result.get('confidence', 0) > 80:
                        ocr_result['category'] = category_result.get('category')
            except Exception as e:
                print(f"⚠️  AI categorization failed: {e}")
                # Continue with OCR-only result
        
        return ocr_result


# Global singleton instance
ocr_service = OCRService()
