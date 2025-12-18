# 🚗 Driver Fatigue Detector

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**An intelligent real-time driver fatigue detection system using computer vision and facial landmark analysis**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Project Structure](#-project-structure) • [Technologies](#-technologies) • [License](#-license)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Technologies](#-technologies)
- [Configuration](#-configuration)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The **Driver Fatigue Detector** is an advanced computer vision application designed to monitor driver alertness in real-time. By analyzing facial landmarks and calculating eye and mouth aspect ratios, the system can detect signs of drowsiness, yawning, and fatigue, triggering immediate alerts to help prevent accidents.

### Key Capabilities

- ✅ **Real-time face detection** using Haar Cascade classifiers
- ✅ **Facial landmark tracking** with 68-point detection
- ✅ **Eye Aspect Ratio (EAR)** calculation for blink detection
- ✅ **Mouth Aspect Ratio (MAR)** calculation for yawn detection
- ✅ **Visual and audio alerts** when fatigue is detected
- ✅ **Firebase integration** for data logging and remote monitoring
- ✅ **Modern GUI** with real-time statistics and visual feedback
- ✅ **Raspberry Pi compatible** version for embedded systems

---

## ✨ Features

### 🎥 Real-Time Monitoring
- Live video feed processing with OpenCV
- Real-time facial landmark detection
- Continuous monitoring of driver state

### 📊 Advanced Detection Algorithms
- **Eye Aspect Ratio (EAR)**: Detects eye closure and blink patterns
- **Mouth Aspect Ratio (MAR)**: Identifies yawning behavior
- **Fatigue Scoring**: Combines multiple metrics for accurate detection

### 🔔 Alert System
- Visual indicators on GUI
- Audio alerts (WAV file playback)
- Configurable alert thresholds

### ☁️ Cloud Integration
- Firebase Realtime Database integration
- Real-time data synchronization
- Alert logging and history tracking
- Device status monitoring

### 🖥️ User Interface
- Modern, dark-themed GUI built with Tkinter
- Real-time statistics display:
  - Current EAR (Eye Aspect Ratio)
  - Blink count
  - Yawn count
  - Fatigue status
  - Progress indicators
- Camera source selection
- Start/Stop controls

---

## 🔬 How It Works

### Detection Pipeline

1. **Face Detection**: Uses Haar Cascade classifier to detect faces in the video stream
2. **Landmark Detection**: Applies dlib's 68-point facial landmark predictor
3. **Feature Extraction**:
   - Extracts eye coordinates (left and right)
   - Extracts mouth coordinates
4. **Ratio Calculation**:
   - **EAR (Eye Aspect Ratio)**: Calculates the ratio of vertical to horizontal eye distances
   - **MAR (Mouth Aspect Ratio)**: Calculates the ratio of vertical to horizontal mouth distances
5. **Fatigue Detection**:
   - Monitors EAR values for prolonged eye closure
   - Monitors MAR values for yawning
   - Tracks consecutive frames below thresholds
6. **Alert Triggering**: Activates visual and audio alerts when fatigue is detected

### Mathematical Formulas

**Eye Aspect Ratio (EAR)**:
```
EAR = (|p2-p6| + |p3-p5|) / (2 × |p1-p4|)
```
Where p1-p6 are eye landmark points.

**Mouth Aspect Ratio (MAR)**:
```
MAR = Vertical Distance / Horizontal Distance
```

---

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- Webcam or camera device
- Internet connection (for Firebase features)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Driver-Fatigue-Detector.git
cd Driver-Fatigue-Detector
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required Packages:**
- `opencv-python==4.0.0.21` - Computer vision library
- `dlib==19.16.0` - Facial landmark detection
- `numpy==1.15.4` - Numerical computing
- `scipy==1.2.0` - Scientific computing
- `imutils==0.5.2` - Image processing utilities
- `playsound==1.2.2` - Audio playback
- `pyrebase` - Firebase integration (if using Firebase features)

### Step 3: Download Required Models

The project requires the following model files:

1. **Haar Cascade XML**: Usually included with OpenCV installation
2. **dlib Shape Predictor**: Download from [dlib.net](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)

   ```bash
   # Extract and place in models/ directory
   # models/shape_predictor_68_face_landmarks.dat
   ```

### Step 4: Configure Firebase (Optional)

If you want to use Firebase features:

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Realtime Database
3. Update `core/firebase.py` with your Firebase configuration:
   ```python
   FIREBASE_CONFIG = {
       "apiKey": "your-api-key",
       "authDomain": "your-project.firebaseapp.com",
       "databaseURL": "your-database-url",
       "storageBucket": "your-project.appspot.com",
   }
   ```

---

## 🚀 Usage

### Running the Application

#### Standard UI Version

```bash
cd Driver-Fatigue-Detector_UI
python main.py
```

#### Raspberry Pi Version

```bash
cd Driver-Fatigue-Detector_Raspberry
python main.py
```

### Using the GUI

1. **Start Detection**: Click the "START" button to begin monitoring
2. **Select Camera**: Use the camera selection dropdown if multiple cameras are available
3. **Monitor Statistics**: Watch the real-time metrics in the GUI:
   - EAR value (should be above threshold when eyes are open)
   - Blink count
   - Yawn count
   - Fatigue status
4. **Alerts**: When fatigue is detected, you'll see:
   - Visual indicators on the GUI
   - Audio alert sound
   - Firebase alert (if configured)
5. **Stop Detection**: Click "STOP" to pause monitoring
6. **Reset**: Use "RESET" to clear counters

### Camera Setup

- Ensure your camera is connected and accessible
- Position the camera to capture your face clearly
- Good lighting improves detection accuracy
- Maintain appropriate distance from camera (30-60 cm recommended)

---

## 📁 Project Structure

```
Driver-Fatigue-Detector/
│
├── README.md                          # Project documentation
├── LICENSE                            # MIT License
├── requirements.txt                   # Python dependencies
│
├── Driver-Fatigue-Detector_UI/       # Standard UI version
│   ├── main.py                       # Application entry point
│   ├── core/                         # Core functionality
│   │   ├── detector.py              # Face and landmark detection
│   │   ├── calculation.py           # EAR/MAR calculations
│   │   ├── firebase.py              # Firebase integration
│   │   └── sound.py                 # Audio alert handling
│   ├── gui/                          # GUI components
│   │   ├── gui_main.py              # Main GUI window
│   │   └── gui_update.py            # GUI update logic
│   ├── models/                       # ML models
│   │   ├── haarcascade_frontalface_default.xml
│   │   └── shape_predictor_68_face_landmarks.dat
│   └── assets/                       # Assets
│       └── Alert.wav                # Alert sound file
│
└── Driver-Fatigue-Detector_Raspberry/ # Raspberry Pi version
    ├── main.py
    ├── core/
    ├── gui/
    ├── models/
    └── assets/
```

---

## 🛠️ Technologies

### Core Technologies
- **Python 3.7+** - Programming language
- **OpenCV** - Computer vision and image processing
- **dlib** - Machine learning and facial landmark detection
- **NumPy** - Numerical computations
- **SciPy** - Scientific computing and distance calculations

### GUI Framework
- **Tkinter** - Python GUI toolkit
- **PIL/Pillow** - Image processing for GUI

### Cloud Services
- **Firebase Realtime Database** - Cloud data storage and synchronization
- **Pyrebase** - Python wrapper for Firebase

### Audio
- **playsound** - Audio file playback

---

## ⚙️ Configuration

### Detection Thresholds

You can adjust detection sensitivity by modifying threshold values in the code:

- **EAR Threshold**: Lower values = more sensitive to eye closure
- **MAR Threshold**: Higher values = more sensitive to yawning
- **Consecutive Frames**: Number of frames below threshold before alert

### Alert Settings

- Modify `Alert.wav` in the `assets/` folder to change alert sound
- Adjust alert frequency and duration in the code

### Firebase Settings

Configure device ID, driver credentials, and database paths in `core/firebase.py`:

```python
DEVICE_ID = "device_01"
DRIVER_EMAIL = "your-email@example.com"
DRIVER_PASSWORD = "your-password"
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Contribution Guidelines

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **dlib** - For facial landmark detection models
- **OpenCV** - For computer vision capabilities
- **Firebase** - For cloud infrastructure
- The open-source community for inspiration and support

---

## 📧 Contact & Support

For questions, issues, or contributions, please open an issue on GitHub.

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star! ⭐**

Made with ❤️ for safer roads

</div>

