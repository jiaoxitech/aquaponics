import requests
import bluetooth
import datetime
import time


BTMAC = '98:D3:32:30:86:CD'
BTPORT = 1
btsocket = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
btsocket.connect((BTMAC,BTPORT))

controlMap = {
  1: {0: 'a', 1: 'b'},
  2: {0: 'c', 1: 'd'},
  3: {0: 'e', 1: 'f'},
  4: {0: 'g', 1: 'h'},
  5: {0: 'i', 1: 'j'},
  6: {0: 'k', 1: 'l'},
  7: {0: 'm', 1: 'n'},
  8: {0: 'o', 1: 'p'}
}


req = requests.get('https://fishfarm.club/relay')


for r in req.json():
  relay = r['relay']
  status = r['status']
  timeOn = r['timeOn']
  timeOff = r['timeOff']
  allDay = r['allDay']
  if status == 0:
     btsocket.send(controlMap[relay][0])
     print '''Relay {} turning off'''.format(relay)
  if status == 1:
     btsocket.send(controlMap[relay][1])
     print '''Relay {} turning on'''.format(relay)
  if status == 2:
     if allDay:
        btsocket.send(controlMap[relay][1])
        print '''Relay {} always on'''.format(relay)
     else:
       if timeOn <= datetime.datetime.now().hour < timeOff:
         btsocket.send(controlMap[relay][1])
         print '''Relay {} turning on'''.format(relay)
       else:
         btsocket.send(controlMap[relay][0])
         print '''Relay {} turning off'''.format(relay)
  # Need to sleep here. Bluetooth connection didn't like fast writes
  time.sleep(0.5)
