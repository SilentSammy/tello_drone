import cv2
from robomaster import robot
import time
from keybrd import *

# Initialize the drone
tl_drone = robot.Drone()
tl_drone.initialize()
tl_flight = tl_drone.flight
tl_camera = tl_drone.camera
tl_camera.start_video_stream(display=False)
tl_camera.set_fps("high")
tl_camera.set_resolution("high")
tl_camera.set_bitrate(6)

# Color detection parameters
lower_hsv = (35, 100, 100)
upper_hsv = (85, 255, 255)

def show_frame(img):
    cv2.namedWindow("Drone", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Drone", cv2.WND_PROP_TOPMOST, 1)
    cv2.resizeWindow("Drone", 400, 400)  # Set the window size to 800x600
    cv2.imshow("Drone", img)
    if cv2.waitKey(1) & 0xFF == 27:
        raise KeyboardInterrupt

def get_obj_pos(frame, lower_hsv, upper_hsv):
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get largest contour of the object
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    cv2.imshow("Mask", mask)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return cx, cy

try:
    while True:
        img = tl_camera.read_cv2_image()
        h, w, _ = img.shape
        pos_pix = get_obj_pos(img, lower_hsv, upper_hsv)
        if pos_pix:
            cx, cy = pos_pix
            norm_pos = ((cx - w / 2) / (w / 2), (cy - h / 2) / (h / 2))
            print(norm_pos)
        cv2.waitKey(1)
        # time.sleep(0.1)  # Adjust the sleep time as needed
finally:
    # Stop the drone
    # tl_flight.land().wait_for_completed()
    tl_drone.close()
    cv2.destroyAllWindows()
    tl_camera.stop_video_stream()