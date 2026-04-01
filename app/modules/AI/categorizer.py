from dotenv import load_dotenv
load_dotenv()
import os 
from openai import OpenAI
import json
from pydantic import BaseModel, field_validator,Field
from tenacity import retry ,stop_after_attempt , wait_exponential
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
CATEGORIES = [
    "electronics",
    "perishable",
    "documents",
    "furniture",
    "hazardous",
    "clothing",
    "other"
]


class CategorizationResult(BaseModel):
    category:str
    confidence:float = Field(ge = 0 , le=1)

    @field_validator("category")
    @classmethod
    def validate_category(cls,value):
        if value not in CATEGORIES:
            raise ValueError("invalid category")
        return value

class ShipmentCategorizer:

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))

    def _call_openai(self,description:str):
        # print("Calling OpenAI once...")
        prompt = f"""
        You are a strict JSON generator.
        Classify the following shipment description into ONE category from:
        {CATEGORIES}

        Return ONLY valid JSON. No explanation.
        Format:
        {{
        "category": "...",
        "confidence": 0.0
        }}

        Description: {description}
        """
        response = self.client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [
                {
                    "role": "system",
                    "content" : "you only return JSON"
                },
                {
                    "role" : "user",
                    "content": prompt
                }
            ]
        )
        content = response.choices[0].message.content.strip()
        return content


    def categorize(self,description:str):
        if not self.client:
            logging.warning("No OpenAI API key found. Using fallback.")
            return CategorizationResult(category = "other",confidence = 0.0) 
        try:
            raw = self._call_openai(description)
            data = json.loads(raw)
            return CategorizationResult(**data)
        
        except Exception as e:
            logging.warning(f"categorization failed {e}")
            return CategorizationResult(category = "other",confidence = 0.0) 

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