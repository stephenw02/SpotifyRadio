import RPi.GPIO as GPIO
import time

redPIN = 25
greenPIN = 24
bluePIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(redPIN, GPIO.OUT)
GPIO.setup(greenPIN, GPIO.OUT)
GPIO.setup(bluePIN, GPIO.OUT)

def light_red():
    GPIO.output(redPIN, GPIO.HIGH)
    GPIO.output(greenPIN, GPIO.LOW)
    GPIO.output(bluePIN, GPIO.LOW)

def light_blue():
    GPIO.output(redPIN, GPIO.LOW)
    GPIO.output(greenPIN, GPIO.LOW)
    GPIO.output(bluePIN, GPIO.HIGH)
    
def light_white():
    GPIO.output(redPIN, GPIO.HIGH)
    GPIO.output(greenPIN, GPIO.HIGH)
    GPIO.output(bluePIN, GPIO.HIGH)
