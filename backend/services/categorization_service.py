"""
Enhanced Categorization Service
Combines rule-based matching with AI-powered categorization
"""
import os
from typing import Optional, Dict, List
from datetime import datetime

from services.ai_service import ai_service, get_all_categories


class CategorizationRule:
    """Rule for matching transactions to categories"""
    
    def __init__(self, keywords: List[str], category: str, priority: int = 0):
        self.keywords = [k.lower() for k in keywords]
        self.category = category
        self.priority = priority
    
    def matches(self, merchant: str) -> bool:
        """Check if merchant matches any keyword"""
        merchant_lower = merchant.lower()
        return any(keyword in merchant_lower for keyword in self.keywords)


class CategorizationService:
    """
    Enhanced categorization service with rule engine and AI fallback
    
    Priority:
    1. Rule-based matching (fast, deterministic)
    2. AI categorization (smart, flexible)
    3. Default category (fallback)
    """
    
    def __init__(self):
        self.rules = self._load_rules()
        self.ai_enabled = ai_service.enabled
        self.stats = {
            "total": 0,
            "rule_matched": 0,
            "ai_categorized": 0,
            "default": 0
        }
    
    def _load_rules(self) -> List[CategorizationRule]:
        """
        Load categorization rules
        
        Rules are sorted by priority (higher first)
        """
        rules = [
            # Food & Dining
            CategorizationRule(
                ["starbucks", "tim hortons", "second cup"],
                "Food - Coffee Shops",
                priority=10
            ),
            CategorizationRule(
                ["mcdonalds", "burger king", "wendys", "kfc", "subway"],
                "Food - Fast Food",
                priority=10
            ),
            CategorizationRule(
                ["costco", "walmart", "loblaws", "sobeys", "metro", "no frills"],
                "Food - Groceries",
                priority=10
            ),
            CategorizationRule(
                ["restaurant", "cafe", "bistro", "grill"],
                "Food - Restaurants",
                priority=5
            ),
            
            # Transportation
            CategorizationRule(
                ["shell", "esso", "petro-canada", "chevron", "gas"],
                "Transportation - Gas",
                priority=10
            ),
            CategorizationRule(
                ["uber", "lyft", "taxi"],
                "Transportation - Public Transit",
                priority=10
            ),
            CategorizationRule(
                ["parking"],
                "Transportation - Parking",
                priority=10
            ),
            
            # Shopping
            CategorizationRule(
                ["amazon", "ebay", "best buy", "apple store"],
                "Shopping - Electronics",
                priority=10
            ),
            CategorizationRule(
                ["zara", "h&m", "gap", "nike", "adidas"],
                "Shopping - Clothing",
                priority=10
            ),
            
            # Bills & Utilities
            CategorizationRule(
                ["rogers", "bell", "telus", "fido"],
                "Bills - Phone",
                priority=10
            ),
            CategorizationRule(
                ["netflix", "spotify", "disney+", "apple music"],
                "Entertainment - Streaming Services",
                priority=10
            ),
            CategorizationRule(
                ["hydro", "electricity", "water", "gas bill"],
                "Housing - Utilities",
                priority=10
            ),
            
            # Health
            CategorizationRule(
                ["pharmacy", "shoppers drug mart", "rexall"],
                "Health - Pharmacy",
                priority=10
            ),
            CategorizationRule(
                ["goodlife", "gym", "fitness"],
                "Health - Fitness",
                priority=10
            ),
            
            # Income
            CategorizationRule(
                ["salary", "payroll", "direct deposit", "payment"],
                "Salary",
                priority=10
            ),
        ]
        
        # Sort by priority (descending)
        return sorted(rules, key=lambda r: r.priority, reverse=True)
    
    def match_rules(self, merchant: str) -> Optional[str]:
        """
        Try to match merchant against rules
        
        Returns:
            Category if matched, None otherwise
        """
        for rule in self.rules:
            if rule.matches(merchant):
                return rule.category
        return None
    
    async def categorize(
        self,
        merchant: str,
        amount: float,
        date: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Categorize a transaction
        
        Returns:
            {
                "category": str,
                "confidence": int,
                "method": "rule" | "ai" | "default",
                "reasoning": str
            }
        """
        self.stats["total"] += 1
        
        # Step 1: Try rule matching
        category = self.match_rules(merchant)
        if category:
            self.stats["rule_matched"] += 1
            return {
                "category": category,
                "confidence": 100,
                "method": "rule",
                "reasoning": f"Matched by rule: {merchant}"
            }
        
        # Step 2: Try AI categorization
        if self.ai_enabled:
            try:
                result = await ai_service.categorize_transaction(
                    merchant=merchant,
                    amount=amount,
                    date=date,
                    description=description
                )
                self.stats["ai_categorized"] += 1
                return {
                    "category": result["category"],
                    "confidence": result["confidence"],
                    "method": "ai",
                    "reasoning": result["reasoning"]
                }
            except Exception as e:
                print(f"AI categorization failed: {str(e)}")
        
        # Step 3: Default category
        self.stats["default"] += 1
        default_category = "Other - Miscellaneous"
        return {
            "category": default_category,
            "confidence": 50,
            "method": "default",
            "reasoning": "No rule or AI match found"
        }
    
    async def categorize_batch(self, transactions: List[Dict]) -> List[Dict]:
        """
        Categorize multiple transactions
        
        Args:
            transactions: List of dicts with merchant, amount, etc.
        
        Returns:
            List of categorization results
        """
        results = []
        for txn in transactions:
            result = await self.categorize(
                merchant=txn.get("merchant", ""),
                amount=txn.get("amount", 0),
                date=txn.get("date"),
                description=txn.get("description")
            )
            results.append({
                "transaction_id": txn.get("id"),
                **result
            })
        return results
    
    def get_stats(self) -> Dict:
        """Get categorization statistics"""
        if self.stats["total"] == 0:
            return {**self.stats, "rule_rate": 0, "ai_rate": 0, "default_rate": 0}
        
        return {
            **self.stats,
            "rule_rate": round(self.stats["rule_matched"] / self.stats["total"] * 100, 1),
            "ai_rate": round(self.stats["ai_categorized"] / self.stats["total"] * 100, 1),
            "default_rate": round(self.stats["default"] / self.stats["total"] * 100, 1)
        }


# Global categorization service instance
categorization_service = CategorizationService()
