from machine import Pin, time_pulse_us
from utime import sleep_us
from math import sqrt

__version__ = '0.3.0'
__author__ = 'Roberto Sánchez'
__license__ = "Apache License 2.0. https://www.apache.org/licenses/LICENSE-2.0"

class HCSR04:
    """
    Driver to use the untrasonic sensor HC-SR04.
    The sensor range is between 2cm and 4m.
    The timeouts received listening to echo pin are converted to OSError('Out of range')
    """
    # echo_timeout_us is based in chip range limit (400cm)
    # air_temp is the temperature of the air. It is setted by default to 20°C
    # air_temp must be defined in order to calculate the speed of sound in the air. It must be passed in Celsius
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=500*2*30, air_temp=20):
        """
        trigger_pin: Output pin to send pulses
        echo_pin: Readonly pin to measure the distance. The pin should be protected with 1k resistor
        echo_timeout_us: Timeout in microseconds to listen to echo pin. 
        By default is based in sensor limit range (4m)
        """
        # the working temperature of the sensor is between -15°C and 70°C according to the datasheet
        self.max_working_temp = 70
        self.min_working_temp = -15

        # speed of sound in the air depends by the temperature of air
        # so first is checked if the air temp is in the working range of the sensor, then will be calculated the speed of sound
        # speed of sound is needed to calculate the distance from the sensor to the object (formula is distance = speed of sound/time)
        self.air_temperature = self._check_air_temp(air_temp)
        self.sound_speed = self._get_sound_speed()
        self.echo_timeout_us = echo_timeout_us

        # Init trigger pin (out)
        self.trigger = Pin(trigger_pin, mode=Pin.OUT, pull=None)
        self.trigger.value(0)

        # Init echo pin (in)
        self.echo = Pin(echo_pin, mode=Pin.IN, pull=None)

    def _check_air_temp(self, temperature):
        """
        Check if air temp is in the working range of the sensor
        """
        try:
            if self.min_working_temp>temperature or self.max_working_temp<temperature:
                raise Exception('temperature out of range')
            return temperature
        except Exception as ex:
            raise

    def _get_sound_speed(self):
        """
        Calculate speed of sound in the air (which depends by air temperature)
        and divide for 1000 in order to convert the speed from m/s to mm/microseconds
        """
        ss = 20.05 * (sqrt(self.air_temperature + 273.15))
        ss = ss / 1000 # conversion from meters / seconds in millimeters / microseconds
        return ss

    def _send_pulse_and_wait(self):
        """
        Send the pulse to trigger and listen on echo pin.
        We use the method `machine.time_pulse_us()` to get the microseconds until the echo is received.
        """
        # Stabilize the sensor
        self.trigger.value(0)
        sleep_us(5)
        self.trigger.value(1)

        # Send a 10us pulse.
        sleep_us(10)
        self.trigger.value(0)

        try:
            pulse_time = time_pulse_us(self.echo, 1, self.echo_timeout_us)
            if pulse_time < 0: # Already impossible, since the minimum should be 2cm
                raise Exception('out of range')
            return pulse_time
        except Exception as ex:
            raise

    def update_air_temp(self, temperature):
        """
        Check if air temp is in the working range of the sensor
        """
        try:
            if self.min_working_temp>temperature or self.max_working_temp<temperature:
                raise Exception('temperature out of range')
            self.air_temperature = temperature
        except Exception as ex:
            raise

    def distance_mm(self):
        """
        Get the distance in milimeters without floating point operations.(?)
        To calculate the distance we get the pulse_time and divide it by 2
        It returns an int
        """
        pulse_time = self._send_pulse_and_wait()
        mm = int( (self.sound_speed * pulse_time) // 2 )
        return mm

    def distance_cm(self):
        """
        Get the distance in centimeters with floating point operations.
        To calculate the distance we get the pulse_time and divide it by 20
        It returns a float
        """
        pulse_time = self._send_pulse_and_wait()
        cms = (self.sound_speed * pulse_time) / 20
        return cms

    def distance_in(self):
        """
        Get the distance in inches with floating point operations.
        To calculate the distance we get the pulse_time and divide it by 50.8 (1in = 2.54cm)
        It returns a float
        """
        pulse_time = self._send_pulse_and_wait()
        inches = (self.sound_speed * pulse_time) / 50.8
        return inches