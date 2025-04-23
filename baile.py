import robomaster
from robomaster import robot


if __name__ == '__main__':
    tl_drone = robot.Drone()
    tl_drone.initialize()

    tl_flight = tl_drone.flight

    # Get battery status
    tl_battery = tl_drone.battery
    battery_info = tl_battery.get_battery()
    print("Drone battery soc: {0}".format(battery_info))

    tl_flight.takeoff().wait_for_completed()
    tl_flight.up(distance=50).wait_for_completed()
    
    for i in range(4):
        # Izquierda
        tl_flight.right(distance=50).wait_for_completed()
        print(i, "der")

        # Derecha
        tl_flight.left(distance=50).wait_for_completed()
        print(i, "izq")

        # Atras
        tl_flight.backward(distance=50).wait_for_completed()
        print(i, "atr")

        tl_flight.rotate(angle = -90).wait_for_completed()
        print(i, "rot")
    
    
    tl_flight.land().wait_for_completed()
    tl_drone.close()