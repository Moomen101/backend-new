import cv2
import requests
import os
import time
import threading
from deepface import DeepFace


BASE_URL = "http://127.0.0.1:8000"
API_MATCH_URL = f"{BASE_URL}/detections/match"
API_MISSING_URL="http://127.0.0.1:8000/missing-persons/all"

RTSP_URL = "rtsp://admin:Miroahlawe@@Yu1@192.168.1.103:554/unicast/c1/s0/live" 


known_faces_data = [] 
is_analyzing = False
matched_person = None 
last_send_time = 0

def load_known_faces():
    global known_faces_data
    print("📡 جاري محاولة الاتصال بالسيرفر...")
    try:
        response = requests.get(API_MISSING_URL)
        missing_persons = response.json()
        
        if not isinstance(missing_persons, list):
            print("⚠️ السيرفر باعت رد مش لستة:", missing_persons)
            return

        for person in missing_persons:
            
            image_url = person.get('image_url') or person.get('photo_url')
            
            if not image_url:
                print(f"⏩ تخطي {person.get('name')}: ملوش صورة.")
                continue

           
            clean_path = image_url.replace("/static/", "")
            image_filename = os.path.basename(clean_path)
            
           
            local_image_path = os.path.join("backend", "uploads", "missing_persons", image_filename)
            
            if os.path.exists(local_image_path):
                print(f"✅ جاري معالجة بصمة: {person['name']}...")
                try:
                    embedding = DeepFace.represent(img_path=local_image_path, 
                                                    model_name="Facenet", 
                                                    enforce_detection=False)[0]["embedding"]
                    
                    known_faces_data.append({
                        "embedding": embedding,
                        "name": person['name'],
                        "id": person.get('person_id') or person.get('id')
                    })
                except Exception as e:
                    print(f"❌ فشل معالجة صورة {person['name']}: {e}")
            else:
                print(f"❓ الصورة مش موجودة في: {local_image_path}")

        print(f"🏁 جاهز! تم تحميل {len(known_faces_data)} شخص.")
        
    except Exception as e:
        print(f"❌ خطأ عام أثناء تحميل البيانات: {e}")

def analyze_face(frame_to_analyze):
    global is_analyzing, matched_person
    
    if len(known_faces_data) == 0:
        is_analyzing = False
        return

    try:
        
        current_face_embedding = DeepFace.represent(img_path=frame_to_analyze, 
                                                    model_name="Facenet",
                                                    enforce_detection=False,
                                                    detector_backend="opencv")[0]["embedding"]
        
        best_match = None
        min_dist = 1.0 
        
        for person_data in known_faces_data:
           
            dist = DeepFace.verify(current_face_embedding, 
                                     person_data["embedding"], 
                                     distance_metric="cosine", 
                                     enforce_detection=False,
                                     model_name="Facenet")['distance']
            
           
            print(f"📊 مسافة التطابق مع {person_data['name']} هي: {dist:.4f}")

            
            if dist < 0.6 and dist < min_dist:
                min_dist = dist
                best_match = person_data
        
        matched_person = best_match 
            
    except Exception as e:
        matched_person = None
        
    is_analyzing = False

cap = cv2.VideoCapture(RTSP_URL) 

if not cap.isOpened():
    print("❌ مش قادر أوصل للكاميرا!")
    exit()


load_known_faces()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    ret, frame = cap.read()
    if not ret: break

    
    frame = cv2.resize(frame, (1280, 720))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
       
        color = (0, 255, 0) if matched_person else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        
        if matched_person:
            cv2.putText(frame, matched_person['name'], (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    
    if len(faces) > 0 and not is_analyzing:
        is_analyzing = True
        threading.Thread(target=analyze_face, args=(frame.copy(),)).start()

    
    if matched_person:
        current_time = time.time()
        if current_time - last_send_time > 15: # بلاغ كل 15 ثانية
            print(f"📸 [MATCH] برسل بلاغ للسيرفر عن {matched_person['name']}...")
            
            temp_file = "dynamic_match.jpg"
            cv2.imwrite(temp_file, frame)
            
            
            payload = {"person_id": matched_person['id'], "confidence_level": 0.98, "location": "Smart Camera Uniview", "camera_id": 1}
            try:
                with open(temp_file, "rb") as f:
                    files = {"image": ("match.jpg", f, "image/jpeg")}
                    resp = requests.post(API_MATCH_URL, data=payload, files=files)
                  
            except Exception as e:
                print("❌ السيرفر مش شغال!")
                
            if os.path.exists(temp_file): os.remove(temp_file)
            last_send_time = current_time

    cv2.imshow("Uniview - All Missing Persons Monitor", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()