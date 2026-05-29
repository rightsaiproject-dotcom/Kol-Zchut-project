import os
from supabase import create_client
from anthropic import Anthropic
from dotenv import load_dotenv

# טעינת משתני סביבה (למקרה שמריצים מקומית)
load_dotenv()

# ניקוי המפתחות מרווחים מיותרים בטעות
supabase_url = os.getenv("SUPABASE_URL", "").strip()
supabase_key = os.getenv("SUPABASE_KEY", "").strip()
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()

# אתחול הלקוחות
db = create_client(supabase_url, supabase_key)
ai = Anthropic(api_key=anthropic_api_key)

def run():
    print("Miner starting...")
    
    # דוגמה ללוגיקה של הבוט
    # כאן יבוא הקוד שלך שמושך מידע או מנתח נתונים
    
    try:
        # בדיקה שהחיבור עובד
        print("Connected to Supabase and Anthropic successfully.")
        # כאן תמשיך עם שאר הלוגיקה שלך...
        
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    run()