import os
import base64
from dotenv import load_dotenv
import anthropic

# ייבוא פונקציית החיפוש שלנו מתוך search.py
from search import search_knowledge

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def extract_main_keyword(text):
    """
    סוכן קטן שכל תפקידו הוא לקרוא את המסמך ולהגיד לנו מה מילת החיפוש הכי טובה
    """
    prompt = f"""
    קרא את הטקסט הרפואי הבא והחזר מילת מפתח אחת בלבד בעברית (מילה אחת!) שהכי רלוונטית לחיפוש זכויות (למשל: סוכרת, אורתופדיה, לב, תאונה, ניידות).
    טקסט: {text[:1000]}
    """
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=20,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()

def analyze_medical_record(text):
    print("\n[1] סוכן האסטרטגיה קורא את התיק ומחלץ מילות מפתח...")
    keyword = extract_main_keyword(text)
    print(f"[2] מחפש ב-Supabase חוקים וזכויות עבור: '{keyword}'...")
    
    # הפעלת גשר החיפוש לסופאבייס
    db_results = search_knowledge(keyword=keyword, limit=3)
    
    # בניית ה"שליף" המשפטי עבור קלוד
    knowledge_context = ""
    if db_results and len(db_results) > 0:
        knowledge_context = "הנה מידע משפטי מדויק שנשלף ממסד הנתונים של המשרד (הסתמך עליו בניתוח הפוטנציאל):\n\n"
        for r in db_results:
            data = r.get("structured_data", {})
            knowledge_context += f"📌 חוק/זכות: {data.get('title', 'ללא כותרת')}\n"
            knowledge_context += f"סיכום: {data.get('summary', '')}\n\n"
    else:
        knowledge_context = "לא נמצא מידע ספציפי במסד הנתונים למקרה זה. הסתמך על הידע הכללי שלך."

    print("[3] כותב דוח אסטרטגי מבוסס מקורות אמת...")
    prompt = f"""
    אתה עורך דין בכיר לזכויות רפואיות בישראל.
    לפניך טקסט מתיק רפואי מצונזר, וכן ידע משפטי עדכני מהמשרד.
    
    === הידע המשפטי (RAG) ===
    {knowledge_context}
    
    === המסמך הרפואי ===
    {text}
    
    החזר דוח מסודר עם: 
    1. ציר זמן רפואי (Timeline).
    2. אבחנות מרכזיות.
    3. פוטנציאל תביעה (חובה להתייחס ולצטט מהידע המשפטי שסופק לך למעלה, אם קיים).
    4. חוסרים (Red Flags).
    """
    
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def analyze_medical_image(image_bytes, media_type):
    print("[2] קורא ומנתח תמונה רפואית...")
    
    # קידוד התמונה לשפה שה-API מבין
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    
    prompt = """
    אתה עורך דין בכיר לזכויות רפואיות בישראל.
    לפניך תמונה של מסמך רפואי (ייתכן שזה צילום מסך או מסמך שצולם בטלפון).
    אנא קרא את הטקסט שמופיע בתמונה ביסודיות והחזר דוח מסודר עם: 
    1. ציר זמן רפואי (Timeline).
    2. האבחנות המרכזיות.
    3. פוטנציאל התביעה.
    4. חוסרים (Red Flags).
    """
    
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2500,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_image,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ],
    )
    return message.content[0].text