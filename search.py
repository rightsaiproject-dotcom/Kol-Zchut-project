import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def search_knowledge(category: str = None, keyword: str = None, limit: int = 5):
    """
    חיפוש חכם בידע
    """
    query = supabase.table("knowledge_items").select("*")

    if category:
        query = query.eq("category", category)

    if keyword:
        # חיפוש בטקסט הגולמי
        query = query.ilike("raw_markdown", f"%{keyword}%")

    response = query.limit(limit).execute()
    return response.data


def print_results(results):
    print(f"\nנמצאו {len(results)} תוצאות:\n")
    for i, r in enumerate(results, 1):
        data = r.get("structured_data", {})
        print(f"{i}. {data.get('title', 'ללא כותרת')}")
        print(f"   קטגוריה: {r.get('category')}")
        print(f"   סיכום: {data.get('summary', '')[:100]}...")
        print(f"   לינק: {r.get('source_url')}")
        print("-" * 50)


if __name__ == "__main__":
    # דוגמה 1: חיפוש לפי קטגוריה
    print("=== חיפוש: נכות כללית ===")
    results = search_knowledge(category="נכות כללית", limit=3)
    print_results(results)

    # דוגמה 2: חיפוש לפי מילת מפתח
    print("\n=== חיפוש: 'ניידות' ===")
    results = search_knowledge(keyword="ניידות", limit=3)
    print_results(results)