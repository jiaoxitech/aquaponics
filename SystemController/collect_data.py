import RPi.GPIO as GPIO
import os
import time
import requests
from envirophat import light, weather, analog

monitor_password = os.environ['MONITOR_PASSWORD']

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
temp_sensor = '/sys/bus/w1/devices/28-00000829846d/w1_slave'

def temp_raw():

    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():

    lines = temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = temp_raw()
    temp_output = lines[1].find('t=')

    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c


GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.OUT)

# Power the water level sensor
GPIO.setup(10, GPIO.OUT)

# Water Pump Relay
GPIO.setup(9, GPIO.OUT)

GPIO.output(22, GPIO.HIGH)
GPIO.output(10, GPIO.HIGH)

try:
  lux = light.light()
  rgb = str(light.rgb())[1:-1].replace(' ', '')
  temp = int(weather.temperature())
  press = int(weather.pressure())
  water1 = analog.read(0)
  waterTemp = read_temp();

  if water1 < 0.5:
    GPIO.output(9, GPIO.HIGH)
  else:
    GPIO.output(9, GPIO.LOW)


  datavals = {
    'password': monitor_password,
    'light': lux,
    'rgb': rgb,
    'temp': temp,
    'press': press,
    'water1': water1,
    'watertemp': waterTemp
    }
  r = requests.post('https://fishfarm.club/monitor/submit', data = datavals)
  GPIO.cleanup()

except KeyboardInterrupt:
  print "Done!"
