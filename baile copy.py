import time
import robomaster
from robomaster import robot


if __name__ == '__main__':
    # Connection
    tl_drone = robot.Drone()
    tl_drone.initialize()
    tl_flight = tl_drone.flight

    # Set the QUAV to takeoff
    tl_flight.takeoff().wait_for_completed()
    
    # Up
    tl_flight.up(distance=50).wait_for_completed()
    
    distance = 50
    for i in range(4):
        # Izquierda
        tl_flight.right(distance=distance).wait_for_completed()
        # time.sleep(1)
        print(i, "Derecha completado")
        
        # Derecha
        tl_flight.left(distance=distance).wait_for_completed()
        print(i, "Izquierda completado")

        # Atras
        tl_flight.backward(distance=distance).wait_for_completed()
        print(i, "Atrás completado")

        # Giro
        tl_flight.rotate(angle=-90).wait_for_completed()
        print(i, "Giro completado")
    
    tl_flight.land().wait_for_completed()
