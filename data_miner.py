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
    # הנה הרשימה שלנו! אפשר להכניס לכאן כמה כתובות שרק נרצה מכל זכות
    urls_to_scan = [
        "https://www.kolzchut.org.il/he/דמי_מחלה",
        "https://www.kolzchut.org.il/he/פיצויי_פיטורים",
        "https://www.kolzchut.org.il/he/חופשה_שנתית",
        "https://www.kolzchut.org.il/he/דמי_אבטלה"
    ]
    
    # הלולאה: הבוט עובר על כל כתובת ברשימה, אחת אחרי השנייה
    for url in urls_to_scan:
        print(f"מתחיל לסרוק את: {url}")
        
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            text = "\n".join([p.get_text() for p in BeautifulSoup(r.text, 'html.parser').find_all('p')])
            
            if not text.strip():
                print(f"⚠️ לא נמצא טקסט, מדלג על: {url}")
                continue # עובר לכתובת הבאה
                
            prompt = "סכם ל-JSON עם שדות: category, title, summary. טקסט: " + text[:1500]
            msg = ai.messages.create(model="claude-sonnet-4-5-20250929", max_tokens=500, messages=[{"role": "user", "content": prompt}])
            
            # ניקוי ה-JSON
            raw_json = msg.content[0].text
            raw_json = raw_json.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw_json)
            
            # שמירה במסד הנתונים
            db.table("knowledge_items").insert({
                "source_url": url, 
                "category": data["category"], 
                "raw_markdown": text,
                "structured_data": data
            }).execute()
            
            print(f"✅ נשאב ונשמר בהצלחה: {url}")
            
        except Exception as e:
            print(f"❌ שגיאה בסריקת {url}: {e}")

if __name__ == "__main__":
    run()