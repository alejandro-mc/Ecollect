#!/usr/bin/env python
import os
from time import sleep

dt = 10 #delay before collecting next data point
while True:
    os.system('sudo python collect-sensor-data3.py')
    sleep(dt)
