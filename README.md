# DJI Tello Object Following using Fuzzy Logic & Computer Vision

This project implements an autonomous object-tracking system for the **DJI Tello Drone**. It utilizes **Computer Vision (OpenCV)** to detect objects based on color and applies **Fuzzy Logic Control** to smooth the drone's movements (Yaw, Pitch, Throttle) in real-time.

## 🎥 Project Overview
The system captures the video feed from the Tello drone, processes it to mask a specific color, and calculates the centroid of the object. A Fuzzy Logic Controller then adjusts the drone's speed and orientation to keep the object centered in the frame at a specific distance.

## 📂 File Structure & Description

### Core System
* **`main.py`**
    The main execution script. It connects to the drone, handles the video stream, orchestrates the tracking logic, and sends commands to the Tello. Run this file to start the project.

* **`Color_tracking.py`**
    The computer vision module. It handles image processing tasks such as:
    * Converting frames to HSV color space.
    * Creating masks for the target color.
    * Calculating contours and the center point $(cx, cy)$ of the object.

* **`Fuzzy.py`**
    The "Brain" of the control system. Unlike standard PID, this file implements **Fuzzy Logic** membership functions (e.g., Close, Ideal, Far) to determine the drone's velocity. It makes the drone's movement smoother and more human-like compared to rigid PID controllers.

### Utilities & Tools
* **`hsv_trackbar.py`**
    A calibration tool. Run this script to open a window with sliders (trackbars). It allows you to manually tune the **HSV (Hue, Saturation, Value)** lower and upper bounds to find the perfect color detection settings for your specific environment/lighting.

* **`Response_Monitor.py`**
    A data visualization tool. It is used to plot the system's response (Error vs. Time) or log data. This helps in analyzing how quickly and stably the drone corrects its position when the object moves.

### Archives
* **`Legacy_Control.py`**
    *Legacy/Experimental File*. Contains previous iterations of the control algorithms (likely standard PID or early Fuzzy logic tests). Kept for reference/backup purposes but not used in the final production run.

## 🚀 How to Run

1.  **Install Dependencies**
    Ensure you have Python installed, then install the required libraries:
    ```bash
    pip install djitellopy opencv-python numpy matplotlib scikit-fuzzy
    ```

2.  **Calibrate Color (Optional)**
    If the lighting conditions change, run the trackbar tool to get new HSV values:
    ```bash
    python hsv_trackbar.py
    ```

3.  **Start Tracking**
    Connect your laptop to the Tello Wi-Fi and run:
    ```bash
    python main.py
    ```

## ⚠️ Safety Precautions
* **Emergency Stop:** Always be ready to terminate the script or grab the drone if it behaves unexpectedly.
* **Lighting:** Ensure the environment is well-lit for accurate color detection.
* **Space:** Test in an open area to avoid collisions.

---
*Created for the Final Project on Intelligent Control Systems (Sistem Kendali Cerdas).*
