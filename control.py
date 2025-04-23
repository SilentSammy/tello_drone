import robomaster
import time 
from robomaster import robot

if __name__ == '__main__':
    tl_drone = robot.Drone()
    tl_drone.initialize()

    tl_flight = tl_drone.flight

    # Set the QUAV to takeoff
    tl_flight.takeoff().wait_for_completed()

    # Draw square movement using flight commands
    print("Initiating movement")
    tl_flight.rc(a=30, b=0, c=0, d=0)
    time.sleep(2)
    tl_flight.rc(a=-30, b=0, c=0, d=0)
    time.sleep(2)
    tl_flight.rc(a=0, b=0, c=0, d=0)
    time.sleep(2)
    tl_flight.rc(a=0, b=30, c=0, d=0)
    time.sleep(2)
    tl_flight.rc(a=0, b=-30, c=0, d=0)
    time.sleep(2)
    tl_flight.rc(a=0, b=0, c=0, d=0)
    time.sleep(2)

    # Set the QUAV to land
    tl_flight.land().wait_for_completed()

    # Close resources
    tl_drone.close()
