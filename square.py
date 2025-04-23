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
    square_size = 150  # Size of the square in cm
    tl_flight.up(distance=100).wait_for_completed()
    tl_flight.backward(distance=square_size).wait_for_completed()
    tl_flight.left(distance=square_size).wait_for_completed()
    tl_flight.forward(distance=square_size).wait_for_completed()
    tl_flight.right(distance=square_size).wait_for_completed()

    time.sleep(1)

    # Set the QUAV to land
    tl_flight.land().wait_for_completed()

    # Close resources
    tl_drone.close()
