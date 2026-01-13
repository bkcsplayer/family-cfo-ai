"""
AI Service for Transaction Categorization
Uses OpenRouter (Claude 3.5 Sonnet) or OpenAI for intelligent categorization
"""
import os
import json
import httpx
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Transaction Categories
CATEGORIES = {
    "income": [
        "Salary",
        "Investment Income",
        "Freelance",
        "Other Income"
    ],
    "expenses": {
        "Housing": ["Rent", "Mortgage", "Utilities", "Home Maintenance"],
        "Transportation": ["Gas", "Public Transit", "Car Payment", "Car Maintenance", "Parking"],
        "Food": ["Groceries", "Restaurants", "Coffee Shops", "Fast Food"],
        "Entertainment": ["Streaming Services", "Movies", "Games", "Hobbies"],
        "Shopping": ["Clothing", "Electronics", "Home Goods", "Personal Care"],
        "Health": ["Medical", "Pharmacy", "Fitness", "Insurance"],
        "Bills": ["Phone", "Internet", "Insurance", "Subscriptions"],
        "Education": ["Tuition", "Books", "Courses"],
        "Other": ["Miscellaneous"]
    }
}

def get_all_categories() -> List[str]:
    """Get flat list of all categories"""
    categories = []
    categories.extend(CATEGORIES["income"])
    for main_cat, subcats in CATEGORIES["expenses"].items():
        categories.extend([f"{main_cat} - {sub}" for sub in subcats])
    return categories


class AIService:
    """AI Service for transaction categorization"""
    
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "openrouter")
        self.enabled = False
        
        if self.provider == "openrouter":
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            self.model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
            self.site_url = os.getenv("OPENROUTER_SITE_URL", "http://localhost:3000")
            self.site_name = os.getenv("OPENROUTER_SITE_NAME", "Family CFO")
        else:  # openai
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.base_url = "https://api.openai.com/v1"
            self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        
        if self.api_key:
            self.enabled = True
        else:
            print(f"⚠️  AI Service disabled - No API key found for provider: {self.provider}")
    
    async def categorize_transaction(
        self,
        merchant: str,
        amount: float,
        date: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Categorize a single transaction using AI
        
        Args:
            merchant: Merchant name
            amount: Transaction amount (negative for expenses)
            date: Transaction date (optional)
            description: Additional description (optional)
        
        Returns:
            {
                "category": "Food - Groceries",
                "confidence": 95,
                "reasoning": "Costco is primarily a grocery store",
                "is_income": false
            }
        """
        # Build prompt
        categories_list = get_all_categories()
        
        prompt = f"""Analyze this financial transaction and categorize it accurately.

Transaction Details:
- Merchant: {merchant}
- Amount: ${abs(amount):.2f} ({'income' if amount > 0 else 'expense'})
{f'- Date: {date}' if date else ''}
{f'- Description: {description}' if description else ''}

Available Categories:
{chr(10).join(f'- {cat}' for cat in categories_list)}

Instructions:
1. Choose the MOST APPROPRIATE category from the list above
2. Provide a confidence score (0-100%)
3. Give a brief reasoning for your choice

Respond ONLY with valid JSON in this exact format:
{{
    "category": "exact category name from list",
    "confidence": 95,
    "reasoning": "brief explanation",
    "is_income": false
}}"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # Add OpenRouter specific headers
                if self.provider == "openrouter":
                    headers["HTTP-Referer"] = self.site_url
                    headers["X-Title"] = self.site_name
                
                data = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,  # Lower temperature for more consistent categorization
                    "max_tokens": 200
                }
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract AI response
                ai_response = result["choices"][0]["message"]["content"]
                
                # Parse JSON response
                # Remove markdown code blocks if present
                ai_response = ai_response.strip()
                if ai_response.startswith("```"):
                    ai_response = ai_response.split("```")[1]
                    if ai_response.startswith("json"):
                        ai_response = ai_response[4:]
                    ai_response = ai_response.strip()
                
                categorization = json.loads(ai_response)
                
                # Validate category exists
                if categorization["category"] not in categories_list:
                    # Try to find closest match
                    categorization["category"] = "Other - Miscellaneous"
                    categorization["confidence"] = max(0, categorization["confidence"] - 20)
                
                return categorization
                
        except httpx.HTTPError as e:
            raise Exception(f"AI API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response: {str(e)}")
        except Exception as e:
            raise Exception(f"AI categorization failed: {str(e)}")
    
    async def categorize_batch(
        self,
        transactions: List[Dict]
    ) -> List[Dict]:
        """
        Categorize multiple transactions
        
        Args:
            transactions: List of transaction dicts with merchant, amount, etc.
        
        Returns:
            List of categorization results
        """
        results = []
        for txn in transactions:
            try:
                result = await self.categorize_transaction(
                    merchant=txn.get("merchant", ""),
                    amount=txn.get("amount", 0),
                    date=txn.get("date"),
                    description=txn.get("description")
                )
                results.append({
                    "transaction_id": txn.get("id"),
                    "success": True,
                    **result
                })
            except Exception as e:
                results.append({
                    "transaction_id": txn.get("id"),
                    "success": False,
                    "error": str(e)
                })
        
        return results


# Global AI service instance
ai_service = AIService()
