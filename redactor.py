import os
import base64
from dotenv import load_dotenv
import anthropic

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# 1. הפונקציה הקיימת לטקסט
def redact_medical_text(raw_text):
    print("[1] סוכן הצנזורה סורק את המסמך...")
    prompt = f"""
    אתה סוכן אבטחת מידע. המטרה שלך היא לצנזר כל פרט מזהה אישי (PII).
    החלף: שמות -> [שם_מצונזר], ת.ז -> [תז_מצונזר], כתובות -> [כתובת_מצונזרת], טלפון -> [טלפון_מצונזר].
    אל תשנה נתונים רפואיים. החזר רק את הטקסט המצונזר.
    
    טקסט מקורי:
    {raw_text}
    """
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

# 2. הפונקציה החדשה לתמונות!
def redact_medical_image(image_bytes, media_type):
    print("[1] סוכן הצנזורה סורק את התמונה ומחלץ טקסט מצונזר...")
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    
    prompt = """
    אתה סוכן אבטחת מידע. המטרה שלך היא לקרוא את הטקסט בתמונה הרפואית, ולצנזר ממנו כל פרט מזהה.
    החלף: שמות -> [שם_מצונזר], ת.ז -> [תז_מצונזר], כתובות -> [כתובת_מצונזרת], טלפון -> [טלפון_מצונזר].
    אל תשנה נתונים רפואיים. החזר אך ורק את הטקסט המצונזר שחילצת, ללא שום הקדמה.
    """
    
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2500,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": base64_image}},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
    )
    return message.content[0].text