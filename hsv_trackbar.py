import cv2
import numpy as np
import time
from djitellopy import Tello

def nothing(x):
    pass

def main():
    # Inisialisasi DJI Tello
    tello = Tello()
    tello.connect()
    tello.streamon()

    # Tunggu beberapa saat agar stream siap
    time.sleep(1)
    frame_read = tello.get_frame_read()

    # Buat window HSV resizable
    win_hsv = 'HSV Adjustments'
    cv2.namedWindow(win_hsv, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_hsv, 400, 250)

    # Buat window All Views
    win_all = 'All Views'
    cv2.namedWindow(win_all, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_all, 700, 500)

    # Buat trackbars HSV
    cv2.createTrackbar('H Min', win_hsv, 0, 179, nothing)
    cv2.createTrackbar('H Max', win_hsv, 179, 179, nothing)
    cv2.createTrackbar('S Min', win_hsv, 0, 255, nothing)
    cv2.createTrackbar('S Max', win_hsv, 255, 255, nothing)
    cv2.createTrackbar('V Min', win_hsv, 0, 255, nothing)
    cv2.createTrackbar('V Max', win_hsv, 255, 255, nothing)

    try:
        while True:
            # Ambil frame dari stream
            frame = frame_read.frame
            if frame is None:
                print("Error: Frame Tello tidak terbaca.")
                break

            pure = frame.copy()
            orig = frame.copy()
            h, w = orig.shape[:2]
            center = (w//2, h//2)
            step_x, step_y = w//3, h//3

            # Gambar grid 3x3
            for i in (1, 2):
                cv2.line(orig, (i*step_x, 0), (i*step_x, h), (255, 255, 255), 1)
                cv2.line(orig, (0, i*step_y), (w, i*step_y), (255, 255, 255), 1)

            hsv = cv2.cvtColor(orig, cv2.COLOR_BGR2HSV)
            h_min = cv2.getTrackbarPos('H Min', win_hsv)
            h_max = cv2.getTrackbarPos('H Max', win_hsv)
            s_min = cv2.getTrackbarPos('S Min', win_hsv)
            s_max = cv2.getTrackbarPos('S Max', win_hsv)
            v_min = cv2.getTrackbarPos('V Min', win_hsv)
            v_max = cv2.getTrackbarPos('V Max', win_hsv)

            lower = np.array([h_min, s_min, v_min])
            upper = np.array([h_max, s_max, v_max])

            mask = cv2.inRange(hsv, lower, upper)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                c = max(contours, key=cv2.contourArea)
                M = cv2.moments(c)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    cv2.circle(orig, (cx, cy), 5, (0, 0, 255), -1)
                    cv2.line(orig, center, (cx, cy), (0, 255, 0), 2)
                    row, col = cy // step_y, cx // step_x
                    cv2.putText(orig, f"Cell: {row},{col}", (10, h-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            result = cv2.bitwise_and(orig, orig, mask=mask)

            top = np.hstack((pure, orig))
            bottom = np.hstack((mask_bgr, result))
            all_views = np.vstack((top, bottom))

            cv2.imshow(win_all, all_views)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        tello.streamoff()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()