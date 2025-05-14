import numpy as np
import cv2
from robomaster import robot
import time
from input_man import is_pressed, rising_edge, is_toggled, get_axis
from simple_pid import PID

MOCK = False

def initialize_drone():
    if not MOCK:
        global tl_drone, tl_flight, tl_camera
        # Initialize the drone
        tl_drone = robot.Drone()
        tl_drone.initialize()
        tl_flight = tl_drone.flight
        tl_camera = tl_drone.camera
        tl_camera.start_video_stream(display=False)
        tl_camera.set_fps("high")
        tl_camera.set_resolution("low")
        tl_camera.set_bitrate(6)

        # Get the SDK of the QUAV.
        drone_version = tl_drone.get_sdk_version()
        print("Drone sdk version: {0}".format(drone_version))

        # Get battery status
        tl_battery = tl_drone.battery
        battery_info = tl_battery.get_battery()
        print("Drone battery soc: {0}".format(battery_info))

def takeoff():
    global flight
    if not MOCK:
        tl_flight.takeoff().wait_for_completed()
    flight = True
    print("Takeoff")

def land():
    global flight
    if not MOCK:
        tl_flight.land().wait_for_completed()
    flight = False
    print("Land")

def close():
    if not MOCK:
        tl_drone.close()
    print("Close")

def flip(x='f'):
    if not MOCK:
        tl_flight.flip(x)
    print("Flip", x)

def send_rc(roll, pitch, throttle, yaw):
    send_rc.prev_roll = send_rc.prev_roll if hasattr(send_rc, 'prev_roll') else 0
    send_rc.prev_pitch = send_rc.prev_pitch if hasattr(send_rc, 'prev_pitch') else 0
    send_rc.prev_yaw = send_rc.prev_yaw if hasattr(send_rc, 'prev_yaw') else 0
    send_rc.prev_throttle = send_rc.prev_throttle if hasattr(send_rc, 'prev_throttle') else 0

    # Only update if there's a change in roll or pitch
    if roll == send_rc.prev_roll and pitch == send_rc.prev_pitch and yaw == send_rc.prev_yaw and throttle == send_rc.prev_throttle:
        return
    
    send_rc.prev_roll = roll
    send_rc.prev_pitch = pitch
    send_rc.prev_yaw = yaw
    send_rc.prev_throttle = throttle

    if not MOCK:
        tl_flight.rc(a=roll, b=pitch, c=throttle, d=yaw)
    print(f"Roll: {roll}, Pitch: {pitch}, Throttle: {throttle}, Yaw: {yaw}")

def get_camera_image():
    if not MOCK:
        img = tl_camera.read_cv2_image()
        return img
    return 255 * np.ones((480, 640, 3), dtype=np.uint8)

def show_frame(img, name):
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(name, cv2.WND_PROP_TOPMOST, 1)
    cv2.resizeWindow(name, 400, 400)  # Set the window size to 800x600
    cv2.imshow(name, img)
    if cv2.waitKey(1) & 0xFF == 27:
        raise KeyboardInterrupt

def screenshot(frame):
    import os

    # Static variables
    screenshot.last_time = screenshot.last_time if hasattr(screenshot, 'last_time') else None
    screenshot.dir_path = screenshot.dir_path if hasattr(screenshot, 'dir_path') else "./screenshots/"+time.strftime("%Y-%m-%d_%H-%M-%S")
    screenshot.count = screenshot.count if hasattr(screenshot, 'count') else 0

    # If less than n seconds have passed since the last screenshot, return
    if screenshot.last_time is not None and time.time() - screenshot.last_time < 1:
        return
    screenshot.last_time = time.time()

    # Make the directory if it doesn't exist
    os.makedirs(screenshot.dir_path, exist_ok=True)

    # Save the image
    filename = os.path.join(screenshot.dir_path, f"screenshot_{screenshot.count}.png")
    cv2.imwrite(filename, frame)
    print(f"Screenshot saved: {filename}")

    # Increment the count
    screenshot.count += 1

def manual_control():
    mag = 50
    yaw_mag = 100
    throttle_mag = 75
    
    pitch, roll, yaw, throttle = 0, 0, 0, 0
    
    # Get keyboard input
    k_pit = 1 if is_pressed('w') else -1 if is_pressed('s') else 0
    k_rol = 1 if is_pressed('d') else -1 if is_pressed('a') else 0
    k_yaw = 1 if is_pressed('e') else -1 if is_pressed('q') else 0
    k_thr = 1 if is_pressed('z') else -1 if is_pressed('x') else 0

    # Get controller input
    c_pit = get_axis('LY')
    c_rol = get_axis('LX')
    c_yaw = get_axis('RX')
    c_thr = get_axis('RT') - get_axis('LT') # Right trigger to go up, left trigger to go down

    # Get the maximum absolute value of the inputs while keeping the sign
    pitch = k_pit if abs(k_pit) > abs(c_pit) else c_pit
    roll = k_rol if abs(k_rol) > abs(c_rol) else c_rol
    yaw = k_yaw if abs(k_yaw) > abs(c_yaw) else c_yaw
    throttle = k_thr if abs(k_thr) > abs(c_thr) else c_thr
    
    # Scale the inputs
    pitch = int(pitch * mag)
    roll = int(roll * mag)
    yaw = int(yaw * yaw_mag)
    throttle = int(throttle * throttle_mag)

    return pitch, roll, yaw, throttle

def flip_control():
    return 'f' if rising_edge('i', 'DPAD_UP') else 'b' if rising_edge('k', 'DPAD_DOWN') else 'l' if rising_edge('j', 'DPAD_LEFT') else 'r' if rising_edge('l', 'DPAD_RIGHT') else None

# Initialize the drone objects
tl_drone, tl_flight, tl_camera = None, None, None
initialize_drone()
flight = False

try:
    if flight:
        takeoff()
    while True:
        # Get the camera image
        img = get_camera_image()
        show_frame(img, "Drone")
        if rising_edge('p') or is_toggled('o'):
            screenshot(img)

        # Takeoff and landing control
        if rising_edge('t', 'Y'):
            if flight:
                land()
            else:
                takeoff()

        # Drone Control
        roll, pitch, yaw, throttle = 0, 0, 0, 0
        f = None
        if flight:
            f = flip_control()
            if not f: # Only get the manual control if not flipping
                pitch, roll, yaw, throttle = manual_control()

        # Send the RC command
        send_rc(roll, pitch, throttle, yaw)
        if f:
            flip(f)
finally:
    cv2.destroyAllWindows()
    land()
    close()
