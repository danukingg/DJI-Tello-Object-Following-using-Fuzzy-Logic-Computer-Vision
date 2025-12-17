import time
import cv2
from djitellopy import Tello
from Color_tracking import setup_window, process_frame
from Fuzzy import compute_fuzzy_yaw_vert
from Response_Monitor import ResponseMonitor, TrackingResponse

# Parameter waktu (detik)
STABILIZE_TIME     = 2
NO_DETECT_TIMEOUT  = 10
TRACK_DURATION     = 60
LOST_TIMEOUT       = 10

# --- inisialisasi monitoring ---
yaw_mon  = ResponseMonitor('yaw')
thr_mon  = ResponseMonitor('throttle')
track_h  = TrackingResponse('h_offset', tol=0.05)
track_v  = TrackingResponse('v_offset', tol=0.05)

def main():
    tello = Tello()
    tello.connect()
    print(f"Battery: {tello.get_battery()}%")
    tello.streamon()
    fr = tello.get_frame_read()

    win = setup_window()
    print("Tekan 't' untuk takeoff")
    while cv2.waitKey(1) & 0xFF != ord('t'):
        pass

    tello.takeoff()
    time.sleep(STABILIZE_TIME)
    tello.send_rc_control(0, 0, 0, 0)
    print("Stabilized. Mulai tracking...")

    start = time.time()
    last_seen = None

    while True:
        frame = fr.frame
        if frame is None:
            continue

        display, h_off, v_off, det = process_frame(frame)

        if det:
            yaw, vz = compute_fuzzy_yaw_vert(h_off * 320, v_off * 240)
            # Update monitors
            yaw_mon.update(yaw)
            thr_mon.update(vz)
            track_h.update(h_off)
            track_v.update(v_off)
            last_seen = time.time()
        else:
            yaw, vz = 0, 0

        tello.send_rc_control(0, 0, vz, yaw)
        cv2.imshow(win, display)
        key = cv2.waitKey(1) & 0xFF
        elapsed = time.time() - start

        if key == ord('q') or elapsed > TRACK_DURATION:
            break
        if start + STABILIZE_TIME < time.time() and (time.time() - start) > NO_DETECT_TIMEOUT:
            break
        if last_seen and (time.time() - last_seen) > LOST_TIMEOUT:
            break

    # Print response summaries
    print()  # blank line
    yaw_mon.summary()
    thr_mon.summary()
    track_h.summary()
    track_v.summary()

    tello.land()
    tello.streamoff()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
