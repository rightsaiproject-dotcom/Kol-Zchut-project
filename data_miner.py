import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client
import anthropic
import urllib.parse

load_dotenv()

db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
ai = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_category_pages(category_name, limit=3):
    # חיבור ישיר למערכת מאחורי הקלעים של כל זכות
    url = "https://www.kolzchut.org.il/api.php"
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category_name}",
        "cmlimit": limit,
        "format": "json"
    }
    response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'})
    data = response.json()
    
    pages = []
    if "query" in data and "categorymembers" in data["query"]:
        for item in data["query"]["categorymembers"]:
            pages.append(item["title"])
    return pages

def run():
    # קטגוריית-העל שבחרת: אנשים עם מוגבלויות
    category_name = "אנשים_עם_מוגבלויות"
    print(f"🔍 מתחבר למוח של כל זכות... מחפש דפים תחת: {category_name.replace('_', ' ')}")
    
    pages = get_category_pages(category_name, limit=3)
    
    if not pages:
        print("❌ לא הצלחתי למצוא עמודים תחת הקטגוריה הזו.")
        return
        
    print(f"✅ מצאתי {len(pages)} עמודים בקטגוריה. מתחיל צלילת עומק (Spidering)...")
    
    for title in pages:
        # קידוד השם כדי ששרתים אמריקאים לא יקרסו בגלל העברית
        encoded_title = urllib.parse.quote(title.replace(' ', '_'))
        url = f"https://www.kolzchut.org.il/he/{encoded_title}"
        print(f"📖 שואב נתונים מהעמוד: {title}")
        
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # טריק חכם: שאיבה רק של גוף התוכן כדי למנוע "סלט" של תפריטים
            content_area = soup.find(id="mw-content-text")
            if content_area:
                paragraphs = content_area.find_all(['p', 'h2', 'h3'])
            else:
                paragraphs = soup.find_all(['p', 'h2', 'h3'])
                
            text = "\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            if not text:
                print("⚠️ עמוד ריק מתוכן, מדלג.")
                continue
                
            # שליחה ל-Claude לסידור הפרקים
            prompt = f"""אתה סוכן מידע חכם. קרא את הטקסט הבא וסדר אותו ל-JSON תקין. 
            החזר אובייקט עם השדות:
            1. "category": "{category_name.replace('_', ' ')}"
            2. "title": "{title}"
            3. "chapters": מערך (Array) של פרקים מתוך הטקסט, שבו לכל פרק יש "chapter_title" (שם הפרק) ו-"chapter_summary" (סיכום של 2-3 משפטים).
            
            טקסט לחילוץ:
            {text[:2000]}"""
            
            msg = ai.messages.create(
                model="claude-sonnet-4-5-20250929", 
                max_tokens=1000, 
                messages=[{"role": "user", "content": prompt}]
            )
            
            # ניקוי ה-JSON
            raw_json = msg.content[0].text
            if "```json" in raw_json:
                raw_json = raw_json.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_json:
                raw_json = raw_json.split("```")[1].split("```")[0].strip()
                
            data = json.loads(raw_json)
            
            # שמירה ב-Supabase
            db.table("knowledge_items").insert({
                "source_url": url, 
                "category": data.get("category"), 
                "raw_markdown": text[:5000],
                "structured_data": data
            }).execute()
            
            print(f"✅ הסוכן סיים בהצלחה את '{title}'! העמוד נשמר מחולק לפרקים.")
            
        except Exception as e:
            print(f"❌ שגיאה בסריקה של '{title}': {e}")

if __name__ == "__main__":
    run()
