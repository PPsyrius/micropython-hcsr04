# HC-SR04 Sensor driver in micropython

Micropython driver for the well-known ultrasonic sensor [HC-SR04](https://www.mpja.com/download/hc-sr04_ultrasonic_module_user_guidejohn.pdf)

This improved version of the original library (https://github.com/rsc1975/micropython-hcsr04) has only been tested on Raspberry Pi Pico so far.

## Motivation

The original's maintainer for this library, @rsc1975 hasn't been active for a while. New changes are thus incorporated here instead from the existing repo, this includes:
- Replacing `time` with `utime` for improve efficiency, also only imported needed functions rather than the entire module - as per spotted by @jfdona23
- The incorporation of air temperature calculation (this affects the speed of sound, and thus, the distance) by @trimalcione
- Miscellaneous overall improvements such as `update_air_temp(temp)` and `distance_in()`

The improved version's `distance_mm()` no longer works for environments where there is no floating point capabilities, and thus forked accordingly from the original repo.

## Examples of use:

### How to get the distance

The `distance_cm()` method returns a `float` with the distance measured by the sensor.
```python
from hcsr04 import HCSR04

sensor = HCSR04(trigger_pin=16, echo_pin=0)

distance = sensor.distance_cm()

print('Distance:', distance, 'cm')
```

The `distance_mm()` method  returns the distance in milimeters (`int` type); unlike the original library this no longer works with environment with no floating point capabilities from the usage of `sqrt` function for air temperature calculations.
```python
from hcsr04 import HCSR04

sensor = HCSR04(trigger_pin=16, echo_pin=0)

distance = sensor.distance_mm()

print('Distance:', distance, 'mm')
```

The `distance_in()` method  returns the distance in inches (`float` type).
```python
from hcsr04 import HCSR04

sensor = HCSR04(trigger_pin=16, echo_pin=0)

distance = sensor.distance_in()

print('Distance:', distance, 'in')
```

The default timeout is based on the sensor limit `(4m)`, but we can also define a different timeout, passing the new value in microseconds to the constructor.
```python
from hcsr04 import HCSR04

sensor = HCSR04(trigger_pin=16, echo_pin=0, echo_timeout_us=1000000)

distance = sensor.distance_cm()

print('Distance:', distance, 'cm')
```

### How to change the air temperature for distance calculation

The `update_air_temp(temp)` method validates whether the new input temp is within sensor's usable range `(-15°C to 70°C)` or not using it. The updated value must be in **Celcius**. By default, the temperature used for calculation is set to 20°C.
```python
import utime
from hcsr04 import HCSR04

sensor = HCSR04(trigger_pin=0, echo_pin=1, air_temp=25)
sensor.update_air_temp(26)

while True:
    try:
        distance_cm = sensor.distance_cm()
        distance_mm = sensor.distance_mm()
        print('Distance (cm/mm):', distance_cm, 'cm;\t', distance_mm, 'mm')
    except Exception as ex:
        print('ERROR getting distance:', ex)
    utime.sleep(2)
```

### Error management

When the driver reaches the timeout while is listening the echo pin the error is converted to `Exception('Out of range')`

```python
from hcsr04 import HCSR04

sensor = HCSR04(trigger_pin=16, echo_pin=0, echo_timeout_us=10000)

try:
    distance = sensor.distance_cm()
    print('Distance:', distance, 'cm')
except Exception as ex:
    print('ERROR getting distance:', ex)

```

## List of confirmed supported devices so far:
- Raspberry Pi Pico
