#!/usr/bin/env python3
"""Read and average measurements from the PSS Sun Sensor on a Raspberry Pi 4."""

import struct
import time

from smbus2 import SMBus, i2c_msg


I2C_BUS = 1
I2C_ADDRESS = 0x4A
READ_DELAY = 0.005
SAMPLE_COUNT = 55
SAMPLE_DELAY = 0.01


class SunSensor:
    """I2C interface for the PSS Sun Sensor."""

    def __init__(self, address=I2C_ADDRESS, delay=READ_DELAY, debug=False):
        # Pi 4 I2C bus 1: SDA on physical pin 3, SCL on physical pin 5.
        self.i2c = SMBus(I2C_BUS)
        self.address = address
        self.delay = delay
        self.debug = debug

        # PSD active area is 4 x 4 mm, represented as +/-2 mm.
        self.psd_half_mm = 2.0
        self.psd_range = 1024
        self.mm_per_unit = self.psd_half_mm / self.psd_range

    def _command_then_read(self, command, read_length):
        """Write a command, wait for the sensor, then read its response."""
        try:
            self.i2c.i2c_rdwr(i2c_msg.write(self.address, [command]))
            time.sleep(self.delay)

            response = i2c_msg.read(self.address, read_length)
            self.i2c.i2c_rdwr(response)
            data = bytes(response)

        except Exception as error:
            print("I2C communication error:", error)
            return bytes(read_length)

        if self.debug:
            raw_bytes = ["0x{:02X}".format(byte) for byte in data]
            print("CMD 0x{:02X} -> Raw bytes:".format(command), raw_bytes)

        return data

    def get_raw(self):
        """Read raw PSD electrode values."""
        data = self._command_then_read(0x03, 9)
        response, vx1, vx2, vy1, vy2 = struct.unpack("<BHHHH", data)
        return vx1, vx2, vy1, vy2

    def get_position_mm(self):
        """Read PSD spot position in millimetres and intensity."""
        data = self._command_then_read(0x04, 7)
        response, x, y, intensity = struct.unpack("<BhhH", data)

        x_mm = x * self.mm_per_unit
        y_mm = y * self.mm_per_unit
        return x_mm, y_mm, intensity

    def get_angles_deg(self):
        """Read sensor-reported X/Y angles in degrees and intensity."""
        data = self._command_then_read(0x05, 7)
        response, angle_x, angle_y, intensity = struct.unpack("<BhhH", data)

        return angle_x / 10.0, angle_y / 10.0, intensity

    def get_temperature(self):
        """Read MCU temperature in degrees Celsius."""
        data = self._command_then_read(0x08, 3)
        response, temperature = struct.unpack("<Bh", data)
        return temperature / 10.0

    def close(self):
        """Release the Raspberry Pi I2C bus."""
        self.i2c.close()


def average_readings():
    """Average position, angle, and temperature over 55 sensor readings."""
    sensor = SunSensor(address=I2C_ADDRESS, debug=False)

    position_x_sum = 0.0
    position_y_sum = 0.0
    angle_x_sum = 0.0
    angle_y_sum = 0.0
    temperature_sum = 0.0
    sample_count = 0

    try:
        for _ in range(SAMPLE_COUNT):
            x_mm, y_mm, position_intensity = sensor.get_position_mm()
            angle_x, angle_y, angle_intensity = sensor.get_angles_deg()
            temperature = sensor.get_temperature()

            position_x_sum += x_mm
            position_y_sum += y_mm
            angle_x_sum += angle_x
            angle_y_sum += angle_y
            temperature_sum += temperature

            sample_count += 1
            time.sleep(SAMPLE_DELAY)

        if sample_count == 0:
            return None

        average_x = position_x_sum / sample_count
        average_y = position_y_sum / sample_count
        average_angle_x = angle_x_sum / sample_count
        average_angle_y = angle_y_sum / sample_count
        average_temperature = temperature_sum / sample_count

        print(
            "Pos_avg=({:.2f},{:.2f})mm  Angles_avg=({:.1f},{:.1f})°  "
            "Temp_avg=({:.1f})°C".format(
                average_x,
                average_y,
                average_angle_x,
                average_angle_y,
                average_temperature,
            )
        )

        # Preserve the original return value: average X angle as a string.
        return "{:.1f}".format(average_angle_x)

    finally:
        sensor.close()


if __name__ == "__main__":
    print(average_readings())
