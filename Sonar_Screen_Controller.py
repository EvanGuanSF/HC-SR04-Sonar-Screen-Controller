#!/usr/bin/env python

import time
import pigpio
import signal

from Ranger import ranger

# An exit flaging class to enable cleanup on exit.
class ExitHandler:
  killed = False
  
  def __init__(self):
    # Catch these signals and set the killed flag
    # so that the main loop knows to stop.
    signal.signal(signal.SIGHUP, self.exit_gracefully)
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGQUIT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.killed = True

if __name__ == '__main__':
  # Set up exit handling.
  processKiller = ExitHandler()

  trigPin = 23
  echoPin = 24
  threeVoltOutPin = 25
  isDisplayOnPin = 18

  pingsPerSecond = 10
  # Number of consecutive readings required to trigger
  # and screen on pulse.
  consecPingsRequired = 3
  consecPingsReceived = 0
  
  isOutputOn = False
  isOutputToggling = False
  isDisplayOn = False
  
  activeDistanceMinCM = 5.0
  activeDistanceMaxCM = 40.0
  activeForSeconds = 10.0
  activeUntilTime = time.time()

  pi = pigpio.pi()
  sonar = ranger(pi, trigPin, echoPin)
  pi.set_mode(isDisplayOnPin, pigpio.INPUT)
  pi.set_mode(threeVoltOutPin, pigpio.OUTPUT)

  # Turn the screen off to start with.
  time.sleep(1)
  if pi.read(isDisplayOnPin):
    print(f'{time.strftime("%Y-%m-%d %H:%M:%S")}: Turning screen off...')
    isDisplayOn = True
    pi.write(threeVoltOutPin, 1)
    time.sleep(0.2)
    pi.write(threeVoltOutPin, 0)
    time.sleep(2)

  # Main Loop
  while not processKiller.killed:
    distance = sonar.distanceCM()
    
    # End power pulse on output pin.
    if isOutputToggling:
      pi.write(threeVoltOutPin, 0)
      isOutputToggling = False
      # Sleep to allow the controller to power cycle.
      time.sleep(0.1)
    
    # Check to see if the screen is powered on.
    if pi.read(isDisplayOnPin):
      isDisplayOn = True
    else:
      isDisplayOn = False

    # Distance check.
    if activeDistanceMinCM < distance < activeDistanceMaxCM:
      if isOutputOn:
        activeUntilTime = time.time() + activeForSeconds
      # On pulse
      # Start power-on pulse on output pin.
      if not isOutputOn and not isOutputToggling and not isDisplayOn:
        # Check and update consecPingsRequired.
        if consecPingsReceived < consecPingsRequired:
          consecPingsReceived += 1
        if consecPingsReceived >= consecPingsRequired:
          print(f'{time.strftime("%Y-%m-%d %H:%M:%S")}: Turning screen on...')
          isOutputToggling = True
          isOutputOn = True
          pi.write(threeVoltOutPin, 1)
          activeUntilTime = time.time() + activeForSeconds
          # Sleep to allow the controller to power cycle.
          time.sleep(0.1)
    else:
      consecPingsReceived = 0

    # Off pulse
    # Start power-off pulse on output pin.
    if time.time() > activeUntilTime and isDisplayOn:
      print(f'{time.strftime("%Y-%m-%d %H:%M:%S")}: Turning screen off...')
      isOutputToggling = True
      isOutputOn = False
      pi.write(threeVoltOutPin, 1)

    print("Distance : {0:0.1f}".format(distance))
    print("Active   : {0}".format(isOutputOn))
    print("Screen   : {0}".format(isDisplayOn))
    time.sleep(1.0/pingsPerSecond)

  # User pressed CTRL-C
  # Reset GPIO settings

  print('Screen Controller shutting down...')

  # Turn the screen off.
  time.sleep(1)
  if pi.read(isDisplayOnPin):
    print(f'{time.strftime("%Y-%m-%d %H:%M:%S")}: Turning screen off...')
    isDisplayOn = True
    pi.write(threeVoltOutPin, 1)
    time.sleep(0.2)
    pi.write(threeVoltOutPin, 0)
    time.sleep(2)

  # Cleanup and exit.
  sonar.cancel()
  pi.stop()

