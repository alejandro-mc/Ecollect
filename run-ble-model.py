#!/usr/bin/env python
import re, shutil, os
import pickle
import pandas as pd
from time import sleep

def writeTitles():
    with open('sensordata','w') as sd:
        sd.write('Timestamp, Temp, Pressure, Humid \n')

def rename_previous_files(path):
    if 'sensordata' in os.listdir(path):
        if 'sensordata1' in os.listdir(path):
            a = pd.read_csv('sensordata')
            b = pd.read_csv('sensordata1')
            merged = b.append(a, ignore_index=True)
            merged.to_csv('sensordata1', index=False)
        else:
            os.rename('sensordata','sensordata1')
    else:
        pass
    writeTitles()
                 
def resetCounter():
    try:
        os.system('rm counter')
    except:
        pass
    counter = 0
    pickle.dump(counter,open('counter','wb'))
    return 0
    

dt = 10 #delay before collecting next data point
rename_previous_files('/home/pi/Documents/Final_Model/')
resetCounter()


while True:
    os.system('sudo python collect-sensor-data-run-model.py')
    sleep(dt)
