"""Application for the RaspberryPi Sense HAT"""

import json
import time

from sense_emu import SenseHat

sense = SenseHat()


def read_sensors():
    """Reads all sensors and returns a dictionary"""
    temp = sense.get_temperature()
    humidity = sense.get_humidity()
    pressure = sense.get_pressure()
    orientation = sense.get_orientation()
    accelerometer = sense.get_accelerometer_raw()
    gyro = sense.get_gyroscope_raw()
    mag = sense.get_compass_raw()

    sensor_data = {
        "Temperature": temp,
        "Humidity": humidity,
        "Pressure": pressure,
        "Orientation": orientation,
        "Accelerometer": accelerometer,
        "Gyroscope": gyro,
        "Magnetometer": mag,
    }

    return sensor_data


def display_message(message):
    """Displays a message on the LED matrix"""
    sense.show_message(message, scroll_speed=0.05)


if __name__ == "__main__":
    # Main loop
    while True:
        data = read_sensors()
        print(json.dumps(data, indent=4))

        display_message(f"Temp: {data['Temperature']:.1f}C")

        time.sleep(5)
