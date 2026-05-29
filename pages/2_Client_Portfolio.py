import streamlit as st
import os
import sys
import anthropic

# חיבור לסוכן האסטרטגיה המקורי
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pdf_agent import analyze_medical_record

# --- סוכן הקטלוג: קורא טקסט ומחזיר "מהות, חודש ושנה" ---
# הפקודה @st.cache_data אומרת לסטרימליט לזכור את התוצאה כדי לא לעבוד קשה בכל פעם שהדף מתרענן
@st.cache_data
def get_document_summary(text):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    prompt = f"""
    קרא את הטקסט הרפואי הבא וסכם אותו ב-3 עד 6 מילים בלבד.
    הפורמט חייב להיות: [מהות המסמך], [חודש ושנה].
    לדוגמה: 'סיכום אשפוז, מאי 2026' או 'תוצאות בדיקת MRI, אפריל 2026'.
    אל תוסיף שום מילה מעבר לפורמט הזה.
    
    טקסט:
    {text[:1500]}
    """
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929", 
        max_tokens=50,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

# עיצוב העמוד
st.set_page_config(page_title="תיק מסמכים | Rights OS", page_icon="🗂️", layout="wide")
st.title("🗂️ ניהול תיק מסמכים (Client Portfolio)")
st.markdown("כאן ניתן לצלול למסמכים הספציפיים של לקוח נבחר, לראות את כולם מסודרים, ולנתח אותם.")
st.markdown("---")

pending_dir = "pending_analysis"
if not os.path.exists(pending_dir):
    os.makedirs(pending_dir)

files = [f for f in os.listdir(pending_dir) if f.endswith("_clean.txt")]

if not files:
    st.info("אין כרגע תיקים או מסמכים במערכת.")
else:
    # 1. חילוץ רשימת הלקוחות הייחודיים (לפי ה-ID שהלקוח העלה)
    clients = set()
    for f in files:
        parts = f.replace("_clean.txt", "").split("_")
        if len(parts) > 1:
            clients.add(f"משרד: {parts[0]} | לקוח: {parts[1]}")
    
    # --- מדרג ראשון: בחירת הלקוח ---
    selected_client_str = st.selectbox("1️⃣ בחר תיק לקוח:", list(clients))
    selected_firm_id = selected_client_str.split(" | ")[0].replace("משרד: ", "")
    selected_client_id = selected_client_str.split(" | ")[1].replace("לקוח: ", "")
    
    # סינון הקבצים כך שנראה רק מסמכים של הלקוח הספציפי הזה
    client_files = [f for f in files if f.startswith(f"{selected_firm_id}_{selected_client_id}")]
    
    st.markdown("---")
    st.subheader(f"📄 מסמכים בתיק של לקוח {selected_client_id}")
    
    # 2. יצירת רשימת המסמכים עם תקציר AI (מהות, תאריך)
    doc_options = {}
    for file_name in client_files:
        file_path = os.path.join(pending_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            text_content = f.read()
        
        # הפעלת סוכן הקטלוג שייתן כותרת יפה למסמך
        with st.spinner("מקטלג מסמכים..."):
            summary_title = get_document_summary(text_content)
        
        doc_options[summary_title] = {"file_name": file_name, "content": text_content}
    
    # --- מדרג שני: בחירת המסמך הספציפי מתוך הרשימה המקוטלגת ---
    selected_doc_title = st.selectbox("2️⃣ בחר מסמך לעיון וניתוח:", list(doc_options.keys()))
    
    if selected_doc_title:
        selected_data = doc_options[selected_doc_title]
        
        st.info(f"📁 למעבר אל קובצי המקור בכספת: Firm_Cloud_Storage/Firm_{selected_firm_id}/Client_{selected_client_id}/Originals/")
        
        # חלונית קריאה חבויה
        with st.expander(f"👀 תצוגה מקדימה למסמך המצונזר"):
            st.text(selected_data["content"])
        
        # --- מדרג שלישי: שיגור הניתוח ---
        if st.button("🚀 נתח אסטרטגיה למסמך זה"):
            with st.spinner("המוח מנתח את המסמך..."):
                try:
                    analysis = analyze_medical_record(selected_data["content"])
                    st.success("הפענוח הושלם בהצלחה!")
                    st.container(border=True).markdown(analysis)
                except Exception as e:
                    st.error(f"שגיאה בפענוח: {e}")