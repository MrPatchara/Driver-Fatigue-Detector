import json
import time
import random
import requests

# URL ของ API ที่จะส่งข้อมูลไป
API_URL = "https://driver-fatigue-detection-fkfyaj409-thanapons-projects-1f5c9397.vercel.app/receive-driving-data"

def generate_mockup_data():
    #ฟังก์ชันสร้าง Mockup Data สำหรับการขับขี่
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "data": [
            {
                "yawningCount": random.randint(0, 10),  # สุ่มจำนวนการหาว
                "blinkingCount": random.randint(50, 150),  # สุ่มจำนวนการกระพริบตา
                "steeringWheelReleaseCount": random.randint(0, 5),  # สุ่มการปล่อยพวงมาลัย
                "eyeClosureDuration": random.uniform(5, 30),  # สุ่มเวลาหลับตา (วินาที)
                "fatigueLevel": random.randint(0, 100)  # สุ่มระดับความเหนื่อยล้า (%)
            }
        ]
    }

def send_mockup_data(user_id, id_token):
    #ฟังก์ชันส่ง Mockup Data พร้อม userId และ Token ไปยัง API
    mockup_data = generate_mockup_data()
    payload = {
        "userId": user_id,
        "drivingData": mockup_data
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {id_token}"  # เพิ่ม Token ใน Header
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            print("Data sent successfully:", json.dumps(payload, indent=2))
        else:
            print(f"Failed to send data: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print("Error while sending data:", e)

if __name__ == "__main__":
    USER_ID = "exampleUserId"  # เปลี่ยน User ID ให้ตรงกับ Firebase Auth
    ID_TOKEN = "YOUR_FIREBASE_ID_TOKEN"  # เปลี่ยนเป็น Token ที่รับมาจาก Frontend

    print("Starting Mockup Data Generator...")
    while True:
        send_mockup_data(USER_ID, ID_TOKEN)
        time.sleep(30)  # ส่งข้อมูลทุก ๆ 30 วินาที