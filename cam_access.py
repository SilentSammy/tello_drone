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

try:
    while True:
        img = tl_camera.read_cv2_image()
        cv2.imshow("Drone", img)
        cv2.waitKey(1)
        # time.sleep(0.1)  # Adjust the sleep time as needed
finally:
    # Stop the drone
    # tl_flight.land().wait_for_completed()
    tl_drone.close()
    cv2.destroyAllWindows()
    tl_camera.stop_video_stream()