import RPi.GPIO as GPIO
import argparse

LED_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN, GPIO.OUT)

parser = argparse.ArgumentParser()
parser.add_argument('--set', choices=['on', 'off'], required=True, help='Set LED to On/Off')
args = parser.parse_args()

if args.set == 'on':
	print('[WW] Powerfull IR emmiter is on: this can damadge you eyes!')
	GPIO.output(LED_PIN, GPIO.HIGH)
else:
	print('[II] IR emmiter is turned off.')
	GPIO.output(LED_PIN, GPIO.LOW)
