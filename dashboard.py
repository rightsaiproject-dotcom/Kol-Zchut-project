import streamlit as st
import PyPDF2
# עכשיו אנחנו מייבאים גם את הפונקציה של התמונות
from pdf_agent import analyze_medical_record, analyze_medical_image

st.set_page_config(page_title="Rights OS | לוח בקרה", page_icon="⚖️", layout="wide")

st.title("⚖️ Rights OS")
st.markdown("### מערכת הפעלה למשרדי זכויות רפואיות")
st.markdown("---")

st.subheader("סוכן פענוח רפואי-משפטי (Triage)")
st.write("העלה סיכום אשפוז, מסמך או **צילום מסך**, והמערכת תפיק דוח אסטרטגי.")

# הוספנו תמיכה ב-png, jpg, jpeg
uploaded_file = st.file_uploader("גרור לכאן את התיק הרפואי", type=['txt', 'pdf', 'png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    st.info("הקובץ נטען בהצלחה. ממתין להוראת פענוח...")
    
    if st.button("🚀 נתח אסטרטגיה משפטית"):
        with st.spinner("המוח הרפואי-משפטי מנתח את החומר..."):
            try:
                analysis = ""
                
                # נתב הקבצים - מחליט מה לעשות לפי סוג הקובץ
                if file_extension in ['png', 'jpg', 'jpeg']:
                    # אם זו תמונה - שולחים לפונקציית ה-Vision
                    media_type = f"image/{'jpeg' if file_extension == 'jpg' else file_extension}"
                    image_bytes = uploaded_file.read()
                    analysis = analyze_medical_image(image_bytes, media_type)
                    
                else:
                    # אם זה טקסט או PDF - מחלצים טקסט ושולחים לפונקציה הרגילה
                    medical_text = ""
                    if file_extension == 'txt':
                        medical_text = uploaded_file.read().decode("utf-8")
                    elif file_extension == 'pdf':
                        pdf_reader = PyPDF2.PdfReader(uploaded_file)
                        for page in pdf_reader.pages:
                            if page.extract_text():
                                medical_text += page.extract_text() + "\n"
                    
                    analysis = analyze_medical_record(medical_text)
                
                st.success("הפענוח הושלם בהצלחה!")
                st.markdown("### 📋 דוח אסטרטגיה ופעולה:")
                st.container(border=True).markdown(analysis)
                
            except Exception as e:
                st.error(f"שגיאה בפענוח: {e}")