import os
import shutil

def route_to_firm_storage(file_path, firm_id, client_id):
    print(f"[1] סוכן הניתוב הופעל עבור משרד {firm_id}, לקוח {client_id}...")
    
    # בניית נתיב התיקיות שירכיב את ה"ענן" של משרד עורכי הדין
    base_storage = "Firm_Cloud_Storage"
    firm_folder = os.path.join(base_storage, f"Firm_{firm_id}")
    client_folder = os.path.join(firm_folder, f"Client_{client_id}")
    originals_folder = os.path.join(client_folder, "Originals")
    
    # יצירת התיקיות אם הן לא קיימות
    os.makedirs(originals_folder, exist_ok=True)
    
    # חילוץ שם הקובץ מהנתיב
    filename = os.path.basename(file_path)
    destination_path = os.path.join(originals_folder, filename)
    
    # העתקת הקובץ למקום המאובטח של המשרד (בעתיד: העלאה ל-Google Drive / AWS)
    shutil.copy2(file_path, destination_path)
            
    print(f"[V] הקובץ המקורי נותב ונשמר בהצלחה בכספת של המשרד: {destination_path}")
    return destination_path

if __name__ == "__main__":
    # טסט: ניקח את המסמך הפיקטיבי שלנו ונעביר אותו ל"ענן" של משרד 1001, לקוח A-552
    test_file = "sample.txt"
    
    if not os.path.exists(test_file):
        print(f"שגיאה: לא מצאתי את הקובץ {test_file}")
    else:
        route_to_firm_storage(test_file, firm_id="1001", client_id="A-552")