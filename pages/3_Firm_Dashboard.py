import streamlit as st
import os
from datetime import datetime

# הגדרות תצוגה - הפעם אנחנו משתמשים בפריסה רחבה (wide) כדי להציג נתונים יפה
st.set_page_config(page_title="דאשבורד משרד | Rights OS", page_icon="📊", layout="wide")
st.title("📊 לוח בקרה ראשי (Firm Dashboard)")
st.markdown("תמונת מצב כללית של המשרד, סטטוס תיקים ופעילות מסמכים נכנסים.")
st.markdown("---")

# שאיבת הנתונים מתיקיית ההמתנה
pending_dir = "pending_analysis"
os.makedirs(pending_dir, exist_ok=True)
clean_files = [f for f in os.listdir(pending_dir) if f.endswith("_clean.txt")]

# חישוב כמות הלקוחות הייחודיים שיש להם כרגע מסמכים
clients = set()
for f in clean_files:
    parts = f.replace("_clean.txt", "").split("_")
    if len(parts) > 1:
        clients.add(parts[1])

# --- אזור המדדים העליון (Metrics) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="👥 תיקי לקוחות פעילים", value=len(clients))
with col2:
    st.metric(label="📄 מסמכים ממתינים לניתוח", value=len(clean_files))
with col3:
    # מדד שבעתיד יתחבר למערכת התראות (למשל: תביעות שמתקרבות להתיישנות)
    st.metric(label="🔔 התראות מערכת", value="0")

st.markdown("---")
st.subheader("⏱️ פעילות אחרונה במערכת (Log)")

if not clean_files:
    st.info("אין כרגע תיקים נכנסים חדשים במערכת.")
else:
    # בניית טבלת נתונים מסודרת
    activity_data = []
    for file in clean_files:
        parts = file.replace("_clean.txt", "").split("_")
        firm_id = parts[0] if len(parts) > 0 else "לא ידוע"
        client_id = parts[1] if len(parts) > 1 else "לא ידוע"
        
        # משיכת תאריך ושעת יצירת הקובץ
        file_path = os.path.join(pending_dir, file)
        mtime = os.path.getmtime(file_path)
        dt_object = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M")
        
        activity_data.append({
            "לקוח (Client ID)": client_id,
            "מזהה מסמך במערכת": file,
            "תאריך קליטה מאובטחת": dt_object,
            "סטטוס צינזור": "🟢 הושלם בהצלחה",
            "מוכן לניתוח AI": "כן"
        })
        
    # הדפסת הטבלה על המסך בצורה יפה ואינטראקטיבית
    st.dataframe(activity_data, use_container_width=True)