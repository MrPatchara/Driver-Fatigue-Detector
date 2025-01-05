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

# ฟังก์ชันอัปเดตเฟรมจากกล้อง ที่เลือกไว้ใน GUI
def update_frame():
    global COUNTER, alarm_status, alarm_status2, saying, eye_blink_count, yawn_count, eyes_closed, mouth_open, alert_triggered, closed_eye_time, progress_full_count

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
                if closed_eye_time >= 50:  # ถ้าหลับตานานเกิน 5 วินาที (50 เฟรม)
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
                progress_full_count += 1  # เพิ่มจำนวนครั้งที่ progress bar เต็ม
                progress_bar["value"] = 0  # รีเซ็ต progress bar
                progress_count_label.config(text=f"Doze Off Count: {progress_full_count}")  # อัปเดต GUI

    status_label.config(text=status_message, fg=status_color)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = ImageTk.PhotoImage(Image.fromarray(frame))
    video_label.imgtk = img
    video_label.configure(image=img)
    video_label.after(10, update_frame)

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
progress_full_count = 0  # ตัวแปรสำหรับนับจำนวนครั้งที่ progress bar เต็ม

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
root.title("Driver Fatigue Detector")
root.geometry("450x750")

#เพิ่ม เมนู settings ด้านบน
menu = tk.Menu(root)
root.config(menu=menu)
settings_menu = tk.Menu(menu)
menu.add_cascade(label="Settings", menu=settings_menu)
# เพิ่มเมนูเลือกแหล่งภาพจากกล้องที่ต้องการ
def change_camera_source(source):
    global vs
    vs.stop()
    vs = VideoStream(src=source).start()
    time.sleep(1.0)
    print(f"Changed camera source to {source}")
    messagebox.showinfo("Camera Source", f"Changed camera source to {source}")
# เพิ่มเมนูเลือกกล้อง
camera_menu = tk.Menu(settings_menu)
settings_menu.add_cascade(label="Change Camera Source", menu=camera_menu)
camera_menu.add_command(label="Internal Camera", command=lambda: change_camera_source(0))
camera_menu.add_command(label="External Camera", command=lambda: change_camera_source(2))


# Vintage mode colors
bg_color = "#2b2b2b"  # Warm dark brown
fg_color = "#d4af37"  # Golden text
btn_color = "#3c3c3c"  # Dark gray buttons
font_style = ("Courier", 16, "bold")

root.configure(bg=bg_color)
video_label = Label(root, bg=bg_color)
video_label.pack()

status_label = Label(root, text="Status: Monitoring", font=(font_style), fg="white", bg=bg_color)
status_label.pack()

ear_label = Label(root, text="EAR: 0.00", font=(font_style), fg=f"gray", bg=bg_color)
ear_label.pack()

yawn_label = Label(root, text="Yawn: 0.00", font=(font_style), fg="gray", bg=bg_color)
yawn_label.pack()

# เพิ่ม Label แสดงจำนวนครั้ง
blink_count_label = Label(root, text="Close Eye Count: 0", font=(font_style), fg=fg_color, bg=bg_color)
blink_count_label.pack()

yawn_count_label = Label(root, text="Yawn Count: 0", font=(font_style), fg=fg_color, bg=bg_color)
yawn_count_label.pack()

# เพิ่ม Label แสดงจำนวนครั้งที่ Progress bar เต็ม
progress_count_label = Label(root, text="Doze Off Count: 0", font=(font_style), fg="red", bg="black")
progress_count_label.pack()

# เพิ่ม progress bar
progress_bar = ttk.Progressbar(root, length=300, maximum=100, mode="determinate")
progress_bar.pack(pady=10)
# ปรับสไตล์ของ progress bar เป็นแบบ classic windows 98
style = ttk.Style()
style.theme_use('classic')
style.configure("TProgressbar", troughcolor="black", background="red", thickness=30)


# ฟังก์ชันเริ่มวิดีโอ
def start_video():
    start_button.config(state="disabled")  # ปิดปุ่มหลังจากกดเริ่ม
    update_frame()

# เพิ่มปุ่ม Start Video
start_button = tk.Button(root, text="Start Video", font=(font_style), command=start_video, bg=bg_color, fg=fg_color)
start_button.pack(pady=10)

# เพิ่มปุ่ม Reset สำหรับรีเซ็ตค่าต่าง ๆ
def reset_values():
    global eye_blink_count, yawn_count, progress_full_count
    eye_blink_count = 0
    yawn_count = 0
    progress_full_count = 0
    blink_count_label.config(text=f"Close Eye Count: {eye_blink_count}")  # รีเซ็ตจำนวนการกะพริบตา
    yawn_count_label.config(text=f"Yawn Count: {yawn_count}")  # รีเซ็ตจำนวนการหาว
    progress_count_label.config(text=f"Doze Off Count: {progress_full_count}")  # รีเซ็ตจำนวนครั้งที่ progress bar เต็ม
    progress_bar["value"] = 0  # รีเซ็ต progress bar
    status_label.config(text="Status: Monitoring", fg="white")  # รีเซ็ตสถานะ
reset_button = tk.Button(root, text="Reset", font=(font_style), command=reset_values, bg="dark blue", fg=fg_color)
reset_button.pack(pady=10)

# เพิ่มปุ่ม Exit สำหรับออกจากโปรแกรม
def exit_program():
    if messagebox.askokcancel("Exit", "Do you want to exit?"):
        root.destroy()
exit_button = tk.Button(root, text="Exit", font=(font_style), command=exit_program, bg="dark red", fg=fg_color)
exit_button.pack(pady=10)


root.mainloop()
cv2.destroyAllWindows()
vs.stop()


