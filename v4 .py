from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import imutils
import time
import dlib
import cv2
import playsound
import os
import tkinter as tk
from tkinter import Label, messagebox  # ใช้สำหรับ pop-up alert
from tkinter import ttk  # ใช้สำหรับ progress bar
from PIL import Image, ImageTk

# ฟังก์ชันสำหรับเล่นเสียง
def sound_alarm(path):
    global alarm_status
    global alarm_status2
    global saying

    while alarm_status:
        playsound.playsound(path)
    if alarm_status2:
        saying = True
        playsound.playsound(path)
        saying = False

# คำนวณ EAR (Eye Aspect Ratio)
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# EAR เฉลี่ยของตาทั้งสองข้าง
def final_ear(shape):
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)
    ear = (leftEAR + rightEAR) / 2.0
    return (ear, leftEye, rightEye)

# คำนวณระยะห่างของปาก
def lip_distance(shape):
    top_lip = shape[50:53]
    top_lip = np.concatenate((top_lip, shape[61:64]))
    low_lip = shape[56:59]
    low_lip = np.concatenate((low_lip, shape[65:68]))
    top_mean = np.mean(top_lip, axis=0)
    low_mean = np.mean(low_lip, axis=0)
    distance = abs(top_mean[1] - low_mean[1])
    return distance

# ฟังก์ชันอัปเดตเฟรมจากกล้อง
def update_frame():
    global COUNTER, alarm_status, alarm_status2, saying, eye_blink_count, yawn_count, eyes_closed, mouth_open, alert_triggered, closed_eye_time

    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

    status_message = "Status: Normal"
    status_color = "white"

    for (x, y, w, h) in rects:
        rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        ear, leftEye, rightEye = final_ear(shape)
        distance = lip_distance(shape)

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        lip = shape[48:60]
        cv2.drawContours(frame, [lip], -1, (0, 255, 0), 1)

        # ตรวจจับการกะพริบตาค้าง
        if ear < EYE_AR_THRESH:
            COUNTER += 1
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                if not alarm_status:
                    alarm_status = True
                    eye_blink_count += 1
                    if alarm_path:
                        Thread(target=sound_alarm, args=(alarm_path,)).start()
                status_message = "Detected Drowsiness!"
                status_color = "red"
                # เพิ่มการติดตามเวลาที่หลับตา (ค้าง)
                closed_eye_time += 1  # เพิ่มเวลาหลับตา
                if closed_eye_time >= 30:  # ถ้าหลับตานานเกิน 3 วินาที (30 เฟรม)
                    alert_triggered = True
        else:
            COUNTER = 0
            alarm_status = False
            closed_eye_time = 0  # รีเซ็ตเวลาหลับตา
            alert_triggered = False  # รีเซ็ตการเตือน

        # ตรวจจับการหาว
        if distance > YAWN_THRESH:
            if not mouth_open:  # เพิ่มการนับเฉพาะครั้งแรกที่ปากเปิด
                yawn_count += 1
                mouth_open = True  # ตั้งสถานะปากเปิด
                if alarm_path and not alarm_status2 and not saying:
                    alarm_status2 = True
                    Thread(target=sound_alarm, args=(alarm_path,)).start()
            status_message = "Detected Yawn!"
            status_color = "orange"
        else:
            mouth_open = False  # รีเซ็ตสถานะปากปิด
            alarm_status2 = False

        # อัปเดตค่าใน GUI
        ear_label.config(text=f"EAR: {ear:.2f}")
        yawn_label.config(text=f"Yawn: {distance:.2f}")
        blink_count_label.config(text=f"Close Eye Count: {eye_blink_count}")  # แสดงจำนวนการกะพริบตา
        yawn_count_label.config(text=f"Yawn Count: {yawn_count}")

        # อัปเดต progress bar หากหลับตานานเกิน 5 วินาที
        if alert_triggered:
            progress_bar["value"] += 1
            if progress_bar["value"] >= 100:  # เตือนเมื่อ progress bar เต็ม
                status_message = "ALERT: Eyes closed for too long!"
                status_color = "red"
                alert_triggered = False  # รีเซ็ตสถานะ
                progress_bar["value"] = 0  # รีเซ็ต progress bar
                # แสดง pop-up alert เมื่อ progress bar เต็ม
                show_alert()

    status_label.config(text=status_message, fg=status_color)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = ImageTk.PhotoImage(Image.fromarray(frame))
    video_label.imgtk = img
    video_label.configure(image=img)
    video_label.after(10, update_frame)

# ฟังก์ชันแสดง pop-up alert
def show_alert():
    result = messagebox.askquestion("ALERT", "Eyes closed for too long! Do you want to reset the program?")
    if result == "yes":
        reset_program()

# ฟังก์ชันรีเซ็ตโปรแกรม
def reset_program():
    global eye_blink_count, yawn_count, COUNTER, closed_eye_time, alert_triggered

    # รีเซ็ต progress bar
    progress_bar["value"] = 0
    # รีเซ็ตตัวแปรต่าง ๆ
    eye_blink_count = 0
    yawn_count = 0
    COUNTER = 0
    closed_eye_time = 0
    alert_triggered = False
    # อัปเดต GUI
    blink_count_label.config(text=f"Blink Count: {eye_blink_count}")
    yawn_count_label.config(text=f"Yawn Count: {yawn_count}")

# ค่าต่าง ๆ
EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 30
YAWN_THRESH = 20
alarm_status = False
alarm_status2 = False
alert_triggered = False  # ตัวแปรใหม่เพื่อกำหนดเมื่อเริ่มการเตือน
saying = False
COUNTER = 0
alarm_path = "Alert1.WAV"
closed_eye_time = 0  # ตัวแปรสำหรับจับเวลาหลับตา

# ตัวแปรนับจำนวนครั้ง
eye_blink_count = 0  # ตัวแปรนับการกะพริบตา
yawn_count = 0

# ตัวแปรสถานะ
eyes_closed = False  # ตรวจสอบว่าตาหลับอยู่หรือไม่
mouth_open = False  # ตรวจสอบว่าปากเปิด (หาว) อยู่หรือไม่

print("-> Loading the predictor and detector...")
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

print("-> Starting Video Stream")
vs = VideoStream(src=0).start()
time.sleep(1.0)

# GUI Setup
root = tk.Tk()
root.title("ระบบ AI ช่วยตรวจจับความเหนื่อยล้าสำหรับคนขับรถ (Driver Fatigue Detector)")
root.configure(bg="black")

video_label = Label(root, bg="black")
video_label.pack()

status_label = Label(root, text="Status: Monitoring", font=("Helvetica", 16), fg="white", bg="black")
status_label.pack()

ear_label = Label(root, text="EAR: 0.00", font=("Helvetica", 14), fg="white", bg="black")
ear_label.pack()

yawn_label = Label(root, text="Yawn: 0.00", font=("Helvetica", 14), fg="white", bg="black")
yawn_label.pack()

# เพิ่ม Label แสดงจำนวนครั้ง
blink_count_label = Label(root, text="Blink Count: 0", font=("Helvetica", 14), fg="white", bg="black")
blink_count_label.pack()

yawn_count_label = Label(root, text="Yawn Count: 0", font=("Helvetica", 14), fg="white", bg="black")
yawn_count_label.pack()

# เพิ่ม progress bar
progress_bar = ttk.Progressbar(root, length=300, maximum=100, mode="determinate")
progress_bar.pack(pady=10)

update_frame()
root.mainloop()

cv2.destroyAllWindows()
vs.stop()
