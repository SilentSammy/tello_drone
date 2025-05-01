import cv2
from robomaster import robot
import time
from keybrd import *
from simple_pid import PID

# Initialize the drone
tl_drone = robot.Drone()
tl_drone.initialize()
tl_flight = tl_drone.flight
tl_camera = tl_drone.camera
tl_camera.start_video_stream(display=False)
tl_camera.set_fps("high")
tl_camera.set_resolution("high")
tl_camera.set_bitrate(6)

# Store drone states
roll, pitch, yaw, throttle = 0, 0, 0, 0
prev_roll, prev_pitch, prev_yaw, prev_throttle = 0, 0, 0, 0

# Store flight state
flight = False

# Color detection parameters
lower_hsv = (35, 100, 100)
upper_hsv = (85, 255, 255)

# Initialize the PID controller
thr_pid = PID(50, setpoint=0)
yaw_pid = PID(50, setpoint=0)
def show_frame(img, name):
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(name, cv2.WND_PROP_TOPMOST, 1)
    cv2.resizeWindow(name, 400, 400)  # Set the window size to 800x600
    cv2.imshow(name, img)
    if cv2.waitKey(1) & 0xFF == 27:
        raise KeyboardInterrupt

def get_obj_pos(frame, lower_hsv, upper_hsv):
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get largest contour of the object
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    show_frame(mask, "mask")
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return cx, cy

try:
    if flight:
        tl_flight.takeoff().wait_for_completed()
    while True:
        # Get the camera image
        img = tl_camera.read_cv2_image()
        show_frame(img, "Drone")

        h, w, _ = img.shape
        pos_pix = get_obj_pos(img, lower_hsv, upper_hsv)
        if pos_pix:
            cx, cy = pos_pix
            norm_pos = ((cx - w / 2) / (w / 2), (cy - h / 2) / (h / 2))
            print(norm_pos)

        # Takeoff and landing control
        if rising_edge('t'):
            flight = not flight
            if flight:
                tl_flight.takeoff().wait_for_completed()
                print("Takeoff")
            else:
                tl_flight.land().wait_for_completed()
                print("Land")

        # Drone Control
        if flight:
            mag = 50
            yaw_mag = 100
            yaw_mag = 100
            throttle_mag = 75
            if not is_toggled('m'): # Manual mode
                pitch = (1 if is_pressed('w') else -1 if is_pressed('s') else 0) * mag
                roll = (1 if is_pressed('d') else -1 if is_pressed('a') else 0) * mag
                yaw = (1 if is_pressed('e') else -1 if is_pressed('q') else 0) * yaw_mag
                throttle = (1 if is_pressed('z') else -1 if is_pressed('x') else 0) * throttle_mag
            else: # Auto mode
                if pos_pix:
                    throttle = thr_pid(norm_pos[1])
                    yaw = -yaw_pid(norm_pos[0])
                else:
                    throttle = 0
                    yaw = 0

        # Only update if there's a change in roll or pitch
        if roll != prev_roll or pitch != prev_pitch or yaw != prev_yaw or throttle != prev_throttle:
            tl_flight.rc(a=roll, b=pitch, c=throttle, d=yaw)
            print(f"Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}, Throttle: {throttle}")
            prev_roll, prev_pitch, prev_yaw, prev_throttle = roll, pitch, yaw, throttle
        
finally:
    cv2.destroyAllWindows()
    tl_flight.land().wait_for_completed()
    tl_drone.close()
