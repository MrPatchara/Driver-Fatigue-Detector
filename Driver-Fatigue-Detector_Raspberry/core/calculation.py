import numpy as np

#-- Eye Aspect Ratio (EAR) calculation from Mediapipe landmarks
def eye_aspect_ratio_from_landmarks(landmarks, eye_indices):
    """
    คำนวณ EAR จาก Mediapipe landmarks
    eye_indices: list ของ index จุดรอบตา
    """
    try:
        points = np.array([[landmarks[i].x, landmarks[i].y] for i in eye_indices])
        A = np.linalg.norm(points[1] - points[5])
        B = np.linalg.norm(points[2] - points[4])
        C = np.linalg.norm(points[0] - points[3])
        return (A + B) / (2.0 * C) if C != 0 else 0.0
    except:
        return 0.0

#-- Lip distance (MAR) calculation
def lip_distance(landmarks):
    """
    คำนวณ MAR (Mouth Aspect Ratio) จาก Mediapipe landmarks
    """
    try:
        top = np.array([
            (landmarks[13].x + landmarks[14].x) / 2,
            (landmarks[13].y + landmarks[14].y) / 2
        ])
        bottom = np.array([
            (landmarks[17].x + landmarks[18].x) / 2,
            (landmarks[17].y + landmarks[18].y) / 2
        ])
        vertical = np.linalg.norm(top - bottom)

        left = np.array([landmarks[61].x, landmarks[61].y])
        right = np.array([landmarks[291].x, landmarks[291].y])
        horizontal = np.linalg.norm(left - right)

        return vertical / horizontal if horizontal != 0 else 0.0
    except:
        return 0.0
