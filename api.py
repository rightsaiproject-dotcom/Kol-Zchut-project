import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional
from fastapi import FastAPI, Query

load_dotenv()

app = FastAPI(title="Rights Knowledge API")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get("/search")
def search(
    category: Optional[str] = Query(None, description="סנן לפי קטגוריה"),
    keyword: Optional[str] = Query(None, description="חיפוש חופשי"),
    limit: int = Query(5, description="מספר תוצאות מקסימלי")
):
    query = supabase.table("knowledge_items").select("*")

    if category:
        query = query.eq("category", category)
    if keyword:
        query = query.ilike("raw_markdown", f"%{keyword}%")

    response = query.limit(limit).execute()
    return response.data


@app.get("/")
def root():
    return {"message": "Rights Knowledge API is running. Go to /docs for documentation."}