import streamlit as st
import os
import sys
import PyPDF2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from router import route_to_firm_storage
# ייבאנו גם את פונקציית התמונות החדשה
from redactor import redact_medical_text, redact_medical_image

st.set_page_config(page_title="פורטל לקוחות", page_icon="👋")
st.title("שליחת מסמכים למשרד")
st.write("המערכת שלנו מאובטחת. המסמכים המקוריים נשמרים ישירות בכספת המשרד ואינם נשמרים בשרתי המערכת.")

col1, col2 = st.columns(2)
with col1:
    firm_id = st.text_input("מספר משרד (Firm ID):", value="1001")
with col2:
    client_id = st.text_input("מזהה לקוח (Client ID):", value="A-552")

# הוספנו תמיכה ב-png, jpg, jpeg
uploaded_file = st.file_uploader("העלאת מסמך רפואי או תמונה", type=['txt', 'pdf', 'png', 'jpg', 'jpeg'])

if uploaded_file is not None and st.button("שלח בצורה מאובטחת"):
    with st.spinner("מצפין, מנתב ומצנזר את החומר הרגיש..."):
        
        # 1. שמירה זמנית בזיכרון השרת
        temp_path = uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # 2. ניתוב הקובץ המקורי לכספת של עורך הדין
        route_to_firm_storage(temp_path, firm_id, client_id)
        
        # בדיקת סוג הקובץ
        file_extension = temp_path.split('.')[-1].lower()
        clean_text = ""
        
        # 3 + 4. חילוץ וצנזורה - בהתאם לסוג הקובץ
        if file_extension in ['png', 'jpg', 'jpeg']:
            media_type = f"image/{'jpeg' if file_extension == 'jpg' else file_extension}"
            with open(temp_path, "rb") as f:
                image_bytes = f.read()
            # קריאת התמונה והשחרת הפרטים בעזרת Vision
            clean_text = redact_medical_image(image_bytes, media_type)
        else:
            raw_text = ""
            if file_extension == 'txt':
                with open(temp_path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
            elif file_extension == 'pdf':
                pdf_reader = PyPDF2.PdfReader(temp_path)
                for page in pdf_reader.pages:
                    if page.extract_text():
                        raw_text += page.extract_text() + "\n"
            # השחרת הפרטים מטקסט רגיל
            clean_text = redact_medical_text(raw_text)
        
        # 5. שמירת הטקסט הנקי בלבד
        os.makedirs("pending_analysis", exist_ok=True)
        clean_file_path = os.path.join("pending_analysis", f"{firm_id}_{client_id}_clean.txt")
        with open(clean_file_path, "w", encoding="utf-8") as f:
            f.write(clean_text)
            
        # 6. השמדת הקובץ המקורי מהשרתים שלנו
        os.remove(temp_path)
        
        st.success("✅ החומר הועבר בהצלחה! תמונות ומסמכים נשמרו במשרד, וגרסה מצונזרת מחכה לפענוח.")