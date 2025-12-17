import cv2
import numpy as np

# Rentang nilai masking warna dalam format HSV
LOWER_HSV = np.array([110,  154, 122])
UPPER_HSV = np.array([129, 255, 255])

# Batas minimal luas kontur untuk dianggap objek valid
MIN_CONTOUR_AREA = 500  # Sesuaikan sesuai kebutuhan


def setup_window(win_name='Tello Camera Views', width=800, height=600):
    """
    Membuat window tampilan kamera dengan ukuran yang dapat diubah.
    """
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_name, width, height)
    return win_name


def process_frame(frame, lower=LOWER_HSV, upper=UPPER_HSV, min_area=MIN_CONTOUR_AREA):
    """
    Memproses satu frame untuk deteksi objek berwarna tertentu.

    Parameter:
    - frame: citra BGR input
    - lower, upper: ambang HSV untuk masking warna
    - min_area: luas kontur minimal untuk dianggap objek valid

    Return:
    - display: tampilan gabungan (frame asli, overlay, mask, result)
    - h_offset: offset horizontal relatif pusat ([-1,1])
    - v_offset: offset vertikal relatif pusat ([-1,1])
    - detected: True jika objek valid terdeteksi
    """
    h, w = frame.shape[:2]
    step_x, step_y = w // 3, h // 3
    center_x, center_y = w // 2, h // 2

    # Gambar grid overlay
    overlay = frame.copy()
    for i in (1, 2):
        cv2.line(overlay, (i * step_x, 0), (i * step_x, h), (255, 255, 255), 1)
        cv2.line(overlay, (0, i * step_y), (w, i * step_y), (255, 255, 255), 1)

    # Convert ke HSV dan masking
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)

    # Temukan kontur eksternal
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h_offset, v_offset = 0.0, 0.0
    detected = False

    if contours:
        # Pilih kontur terbesar
        c = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(c)
        if area >= min_area:
            M = cv2.moments(c)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                # Tandai titik centroid
                cv2.circle(overlay, (cx, cy), 5, (0, 0, 255), -1)
                # Hitung baris, kolom grid
                row, col = cy // step_y, cx // step_x
                cv2.putText(overlay, f"Cell: {row},{col}", (10, h - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Hitung offset relatif pusat
                h_offset = (cx - center_x) / float(center_x)
                v_offset = (cy - center_y) / float(center_y)
                detected = True
        else:
            # Noise: kontur terlalu kecil
            cv2.putText(overlay, f"Noise: area {int(area)} < {min_area}", (10, h - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Buat tampilan gabungan: asli | overlay di baris atas; mask | result di baris bawah
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    result = cv2.bitwise_and(overlay, overlay, mask=mask)
    top = np.hstack((frame, overlay))
    bottom = np.hstack((mask_bgr, result))
    display = np.vstack((top, bottom))

    return display, h_offset, v_offset, detected
