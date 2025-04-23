import robomaster
import time 
from robomaster import robot


if __name__ == '__main__':
    tl_drone = robot.Drone()
    tl_drone.initialize()

    tl_flight = tl_drone.flight

    # Set the QUAV to takeoff
    # tl_flight.takeoff().wait_for_completed()

    # Add a delay to remain in hover
    print("Remaning in hover")
    # time.sleep(3)

    # Set the QUAV to land
    tl_flight.land().wait_for_completed()

    # Close resources
    tl_drone.close()