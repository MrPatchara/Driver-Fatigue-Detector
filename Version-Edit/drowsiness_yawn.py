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
from tkinter import Label
from PIL import Image, ImageTk

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

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def final_ear(shape):
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)
    ear = (leftEAR + rightEAR) / 2.0
    return (ear, leftEye, rightEye)

def lip_distance(shape):
    top_lip = shape[50:53]
    top_lip = np.concatenate((top_lip, shape[61:64]))
    low_lip = shape[56:59]
    low_lip = np.concatenate((low_lip, shape[65:68]))
    top_mean = np.mean(top_lip, axis=0)
    low_mean = np.mean(low_lip, axis=0)
    distance = abs(top_mean[1] - low_mean[1])
    return distance

def update_frame():
    global COUNTER, alarm_status, alarm_status2, saying

    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

    status_message = "สถานะ: ปกติ"
    status_color = "black"

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

        if ear < EYE_AR_THRESH:
            COUNTER += 1
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                if not alarm_status:
                    alarm_status = True
                    if alarm_path:
                        Thread(target=sound_alarm, args=(alarm_path,)).start()
                status_message = "ตรวจพบการง่วง จอดรถ!"
                status_color = "red"
        else:
            COUNTER = 0
            alarm_status = False

        if distance > YAWN_THRESH:
            status_message = "พบการหาวถ้าง่วงก็ไปนอนไป๊ !"
            status_color = "orange"
            if not alarm_status2 and not saying:
                alarm_status2 = True
                if alarm_path:
                    Thread(target=sound_alarm, args=(alarm_path,)).start()
        else:
            alarm_status2 = False

        ear_label.config(text=f"EAR: {ear:.2f}")
        yawn_label.config(text=f"Yawn: {distance:.2f}")

    status_label.config(text=status_message, fg=status_color)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = ImageTk.PhotoImage(Image.fromarray(frame))
    video_label.imgtk = img
    video_label.configure(image=img)
    video_label.after(10, update_frame)

EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 30
YAWN_THRESH = 20
alarm_status = False
alarm_status2 = False
saying = False
COUNTER = 0
alarm_path = "Alert1.WAV"

print("-> Loading the predictor and detector...")
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

print("-> Starting Video Stream")
vs = VideoStream(src=0).start()
time.sleep(1.0)

# GUI Setup
root = tk.Tk()
root.title("ระบบ AI ช่วยตรวจจับความเหนื่อยล้าสำหรับคนขับรถ (Driver Fatigue Detector)")

video_label = Label(root)
video_label.pack()

status_label = Label(root, text="Status: Monitoring", font=("Helvetica", 16))
status_label.pack()

ear_label = Label(root, text="EAR: 0.00", font=("Helvetica", 14))
ear_label.pack()

yawn_label = Label(root, text="Yawn: 0.00", font=("Helvetica", 14))
yawn_label.pack()

update_frame()
root.mainloop()

cv2.destroyAllWindows()
vs.stop()
