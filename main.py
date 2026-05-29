import os
import json
import time
import logging
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from supabase import create_client, Client
import anthropic

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
firecrawl = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def scrape_page(url: str, max_retries: int = 2):
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"[1] שואב: {url}")
            result = firecrawl.scrape_url(url, formats=['markdown'])
            return result.markdown
        except Exception as e:
            if attempt == max_retries:
                return None
            time.sleep(2)


def process_with_claude(text: str, max_retries: int = 2):
    for attempt in range(max_retries + 1):
        try:
            logger.info("[2] מעבד עם Claude...")
            prompt = f"""
אתה מומחה בכיר למיצוי זכויות רפואיות בישראל.
החזר **רק JSON תקין**.

ה-JSON חייב להכיל בדיוק את השדות הבאים:

{{
  "title": "שם הזכות",
  "summary": "סיכום קצר",
  "eligibility": {{
    "age": "...",
    "disability_percentage": "...",
    "income": "...",
    "other": "..."
  }},
  "required_documents": ["...", "..."],
  "benefits": {{
    "monthly_allowance": "...",
    "other_benefits": "..."
  }},
  "application_process": "...",
  "relevant_laws": ["חוק 1", "חוק 2"],
  "common_rejections": ["סיבה 1", "סיבה 2"],
  "notes": "הערות חשובות לעורך דין"
}}

טקסט:
{text}
"""
            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = message.content[0].text
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            return response_text
        except Exception as e:
            if attempt == max_retries:
                return None
            time.sleep(3)


def save_to_supabase(url: str, category: str, raw_text: str, structured_json_str: str):
    try:
        structured_dict = json.loads(structured_json_str)
        data = {
            "source_url": url,
            "category": category,
            "raw_markdown": raw_text,
            "structured_data": structured_dict
        }
        supabase.table("knowledge_items").insert(data).execute()
        logger.info(f"נשמר: {category}")
    except Exception as e:
        logger.error(f"שגיאה: {e}")


if __name__ == "__main__":
    with open("urls.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    for line in lines:
        if "|" not in line:
            continue
        category, url = line.split("|", 1)
        logger.info(f"\n=== {category} ===")

        raw_text = scrape_page(url)
        if not raw_text:
            continue

        structured = process_with_claude(raw_text)
        if not structured:
            continue

        save_to_supabase(url, category, raw_text, structured)

    logger.info("\n=== הסתיים ===")