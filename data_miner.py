import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client
import anthropic

load_dotenv()

db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
ai = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run():
    url = "https://he.wikipedia.org/wiki/חוק_הביטוח_הלאומי"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    text = "\n".join([p.get_text() for p in BeautifulSoup(r.text, 'html.parser').find_all('p')])
    
    prompt = "סכם ל-JSON עם שדות: category, title, summary. טקסט: " + text[:1500]
    msg = ai.messages.create(model="claude-sonnet-4-5-20250929", max_tokens=500, messages=[{"role": "user", "content": prompt}])
    
    # ניקוי בטוח בשלבים
    raw_json = msg.content[0].text
    raw_json = raw_json.replace("```json", "").replace("```", "").strip()
    
    data = json.loads(raw_json)
    db.table("knowledge_items").insert({"source_url": url, "category": data["category"], "structured_data": data}).execute()
    print("✅ עבד!")

if __name__ == "__main__":
    run()