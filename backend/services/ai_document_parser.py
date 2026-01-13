"""
AI Document Parsing Service
Uses OCR + LLM to extract structured data from scanned documents.
"""
import os
import json
import logging
from typing import Dict, Any, Tuple
from decimal import Decimal
import httpx

logger = logging.getLogger(__name__)

class AIDocumentParser:
    """
    Parses documents using AI (OCR + LLM extraction).
    Supports insurance policies, receipts, bank statements, etc.
    """

    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.ocr_enabled = os.getenv("ENABLE_OCR", "false").lower() == "true"

    async def parse_insurance_document(self, file_path: str) -> Tuple[Dict[str, Any], Decimal]:
        """
        Parse an insurance policy document.

        Returns:
            (parsed_data, confidence_score)
        """
        try:
            # Step 1: OCR extraction (if enabled)
            if self.ocr_enabled:
                extracted_text = await self._extract_text_ocr(file_path)
            else:
                # Mock extraction for development
                extracted_text = self._mock_insurance_text()

            # Step 2: LLM structured extraction
            parsed_data, confidence = await self._extract_insurance_with_llm(extracted_text)

            logger.info(f"Parsed insurance document: confidence={confidence}")
            return parsed_data, confidence

        except Exception as e:
            logger.error(f"Failed to parse insurance document: {e}")
            return self._get_empty_insurance_data(), Decimal("0.0")

    async def _extract_text_ocr(self, file_path: str) -> str:
        """Extract text from image/PDF using OCR (Tesseract)"""
        try:
            import pytesseract
            from PIL import Image

            # Handle PDF conversion if needed
            if file_path.lower().endswith('.pdf'):
                # Use pdf2image for PDF to image conversion
                from pdf2image import convert_from_path
                pages = convert_from_path(file_path, first_page=1, last_page=1)
                if pages:
                    text = pytesseract.image_to_string(pages[0])
                else:
                    text = ""
            else:
                # Direct image OCR
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image)

            return text.strip()
        except ImportError:
            logger.warning("OCR dependencies not installed. Using mock data.")
            return self._mock_insurance_text()
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""

    async def _extract_insurance_with_llm(self, text: str) -> Tuple[Dict[str, Any], Decimal]:
        """Use LLM to extract structured data from insurance document text"""

        if not self.openrouter_api_key:
            logger.warning("No OpenRouter API key. Using fallback extraction.")
            return self._fallback_extraction(text)

        try:
            prompt = f"""Extract structured information from this insurance policy document.
Return ONLY a valid JSON object with these fields:
- provider (string): Insurance company name
- type (string): One of: Auto, Home, Life, Health, Disability
- policy_number (string): Policy ID/number
- coverage_amount (number): Total coverage in dollars
- premium (number): Cost per payment period
- frequency (string): "Monthly" or "Yearly"
- renewal_date (string): Date in YYYY-MM-DD format
- insured_item (string): What is insured (e.g., vehicle model, property address)
- reimbursement_details (object): Map of coverage items to reimbursement ratios (0-1)
- notes (string): Additional relevant details

Document text:
{text[:3000]}

Return JSON only, no explanation:"""

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3.5-sonnet",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1
                    }
                )
                response.raise_for_status()
                result = response.json()

                # Extract JSON from LLM response
                content = result["choices"][0]["message"]["content"]

                # Clean markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                parsed_data = json.loads(content.strip())

                # Calculate confidence based on completeness
                confidence = self._calculate_confidence(parsed_data)

                return parsed_data, Decimal(str(confidence))

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self._fallback_extraction(text)

    def _fallback_extraction(self, text: str) -> Tuple[Dict[str, Any], Decimal]:
        """Simple fallback extraction using keyword matching"""
        data = self._get_empty_insurance_data()
        confidence = Decimal("0.3")  # Low confidence for fallback

        # Simple keyword extraction
        text_lower = text.lower()

        if "sun life" in text_lower:
            data["provider"] = "Sun Life"
            confidence += Decimal("0.1")
        elif "manulife" in text_lower:
            data["provider"] = "Manulife"
            confidence += Decimal("0.1")

        if "health" in text_lower or "dental" in text_lower:
            data["type"] = "Health"
            confidence += Decimal("0.1")
        elif "auto" in text_lower or "vehicle" in text_lower:
            data["type"] = "Auto"
            confidence += Decimal("0.1")

        return data, confidence

    def _calculate_confidence(self, parsed_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data completeness"""
        required_fields = ["provider", "type", "premium"]
        optional_fields = ["policy_number", "coverage_amount", "renewal_date", "insured_item"]

        score = 0.0

        # Required fields: 0.6 points total
        for field in required_fields:
            if parsed_data.get(field):
                score += 0.2

        # Optional fields: 0.4 points total
        for field in optional_fields:
            if parsed_data.get(field):
                score += 0.1

        return min(1.0, score)

    def _get_empty_insurance_data(self) -> Dict[str, Any]:
        """Return empty insurance data structure"""
        return {
            "provider": "",
            "type": "Health",
            "policy_number": "",
            "coverage_amount": 0,
            "premium": 0,
            "frequency": "Monthly",
            "renewal_date": None,
            "insured_item": "",
            "reimbursement_details": {},
            "notes": ""
        }

    def _mock_insurance_text(self) -> str:
        """Mock insurance document text for development"""
        return """
        SUN LIFE FINANCIAL
        Health Insurance Policy

        Policy Number: SL-2024-12345
        Coverage Amount: $50,000
        Premium: $250/month
        Renewal Date: 2026-06-30

        Coverage Details:
        - Dental: 80% reimbursement
        - Vision: 50% reimbursement
        - Prescription: 90% reimbursement

        Insured: Family Plan
        """

# Singleton instance
ai_parser = AIDocumentParser()
