from dotenv import load_dotenv
import os
import re
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, field_validator, Field
from openai import OpenAI
import json
load_dotenv(override=True)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

CATEGORIES = [
    "electronics",
    "perishable",
    "documents",
    "furniture",
    "hazardous",
    "clothing",
    "other"
]

CATEGORY_KEYWORDS = {
    "electronics": (
        "battery",
        "camera",
        "charger",
        "computer",
        "electronic",
        "headphone",
        "iphone",
        "laptop",
        "macbook",
        "mobile",
        "monitor",
        "phone",
        "tablet",
        "tv",
    ),
    "perishable": (
        "bakery",
        "dairy",
        "fish",
        "flower",
        "food",
        "fresh",
        "fruit",
        "meat",
        "medicine",
        "perishable",
        "produce",
        "vegetable",
    ),
    "documents": (
        "certificate",
        "contract",
        "document",
        "file",
        "invoice",
        "legal",
        "letter",
        "paper",
        "passport",
        "records",
    ),
    "furniture": (
        "bed",
        "cabinet",
        "chair",
        "couch",
        "desk",
        "dining",
        "furniture",
        "mattress",
        "sofa",
        "table",
        "wardrobe",
    ),
    "hazardous": (
        "acid",
        "aerosol",
        "chemical",
        "explosive",
        "flammable",
        "fuel",
        "hazard",
        "hazardous",
        "paint",
        "toxic",
    ),
    "clothing": (
        "apparel",
        "clothes",
        "clothing",
        "dress",
        "garment",
        "jacket",
        "pants",
        "shirt",
        "shoes",
        "textile",
    ),
}


class CategorizationResult(BaseModel):
    category:str
    confidence:float = Field(ge = 0 , le=1)

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, value):
        value = str(value).strip().lower()
        if value not in CATEGORIES:
            raise ValueError(f"invalid category '{value}', must be one of {CATEGORIES}")
        return value

class ShipmentCategorizer:

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def _fallback_categorize(self, description: str) -> CategorizationResult:
        """Keyword-based fallback when OpenAI is unavailable.
        
        Uses whole-word regex matching (\\b) to avoid false positives like
        'tv' matching 'activity' or 'bed' matching 'embedded'.
        Scores all categories and picks the one with the most keyword hits.
        """
        text = (description or "").lower()
        scores: dict[str, int] = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            hits = sum(
                1 for kw in keywords
                if re.search(r'\b' + re.escape(kw) + r'(?:s|es)?\b', text)
            )
            if hits > 0:
                scores[category] = hits

        if not scores:
            return CategorizationResult(category="other", confidence=0.0)

        best = max(scores, key=lambda c: scores[c])
        confidence = min(0.60 + (scores[best] - 1) * 0.10, 0.80)
        return CategorizationResult(category=best, confidence=round(confidence, 2))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))

    def _call_openai(self,description:str):
        # print("Calling OpenAI once...")
        prompt = f"""
        You are a strict JSON generator.
        Classify the following shipment description into ONE category from:
        {CATEGORIES}

        Pick the closest matching category. Use "other" only when none of the
        listed categories match the description.

        Return ONLY valid JSON. No explanation.
        Format:
        {{
        "category": "...",
        "confidence": 0.0
        }}

        Description: {description}
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You classify shipment descriptions. Return only valid JSON. "
                        "Do not choose 'other' if electronics, perishable, documents, "
                        "furniture, hazardous, or clothing reasonably fits."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        content = response.choices[0].message.content.strip()
        # Strip markdown code fences in case model wraps output (defence-in-depth)
        content = re.sub(r'^```(?:json)?\s*', '', content, flags=re.IGNORECASE)
        content = re.sub(r'```\s*$', '', content)
        return content.strip()


    def categorize(self,description:str):
        if not self.client:
            logger.warning("categorization.openai.skipped reason=no_openai_key")
            return self._fallback_categorize(description)
        try:
            raw = self._call_openai(description)
            data = json.loads(raw)
            return CategorizationResult(**data)
        except Exception as e:
            logger.error("categorization.failed description=%r error=%s", description[:60], e)
            return self._fallback_categorize(description)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    categorizer = ShipmentCategorizer()

    samples = [
        "iPhone and laptop shipment",
        "fresh vegetables and fruits",
        "legal contract documents",
        "wooden dining table",
        "flammable chemicals",
        "random unknown item"
    ]

    for s in samples:
        result = categorizer.categorize(s)
        print(f"{s} → {result}")
