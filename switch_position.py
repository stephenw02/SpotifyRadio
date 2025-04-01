import RPi.GPIO as GPIO
import time
from light_controller import light_red, light_blue, light_white

PIN1 = 17
PIN2 = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read_switch():
    state1 = GPIO.input(PIN1)
    state2 = GPIO.input(PIN2)
    
    if state1 == GPIO.LOW:
        light_red()
        return "Position 1 - ON"
    elif state2 == GPIO.LOW:
        light_blue()
        return "Position 2 - ON"
    else:
        light_white()
        return "OFF"
    
try:
    while True:
        print("Switch State: ", read_switch())
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print('GPIO pins cleaned up')