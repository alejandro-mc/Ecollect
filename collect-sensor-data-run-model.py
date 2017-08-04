#!/usr/bin/env python
# Example of interaction with a BLE UART device using a UART service
# implementation.
# Author: Tony DiCola
import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART
from time import sleep, strftime, time
import time
import pickle
import urllib2
import json


# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()

num_of_feathers = 1

def get_current_conditions():
    owm = urllib2.urlopen('http://api.openweathermap.org/data/2.5/weather?zip=10031,us&appid=c09d23aa0da6ee0781c93da975ea4314')
    json_string = owm.read()
    parsed_json = json.loads(json_string)
    current_cond = open('CurrentConditions.csv','a+')
    a = str(strftime('%m-%d-%Y %H:%M'))
    h = str(',')
    b = str(parsed_json['clouds']['all'])
    c = str(parsed_json['main']['temp'])
    d = str(parsed_json['wind']['speed'])
    e = str('\n')
    current_cond.write(str(a+h+b+h+c+h+d+e))
    current_cond.close()
    owm.close()

def get_1day_forecast(forecast_hours):
    wunderf = urllib2.urlopen('http://api.wunderground.com/api/96339b26bc65f75d/hourly/q/NY/Harlem.json')
    json_string = wunderf.read()
    parsed_json = json.loads(json_string)
    forecast = open('1DayForecast.csv','a+')
    counter = 0
    while counter < forecast_hours:
        forecast = open('1DayForecast.csv','a+')
        a = str(parsed_json['hourly_forecast'][counter]['FCTTIME']['mon'])
        b = str(parsed_json['hourly_forecast'][counter]['FCTTIME']['mday'])
        c = str(parsed_json['hourly_forecast'][counter]['FCTTIME']['year'])
        d = str(parsed_json['hourly_forecast'][counter]['FCTTIME']['hour'])
        e = str(parsed_json['hourly_forecast'][counter]['FCTTIME']['min'])
        f = str(parsed_json['hourly_forecast'][counter]['sky'])
        g = str(parsed_json['hourly_forecast'][counter]['temp']['english'])
        h = str(parsed_json['hourly_forecast'][counter]['wspd']['english'])
        i = str('/')
        j = str(',')
        k = str('\n')
        l = str(' ')
        m = str(':')
        forecast.write(str(a+i+b+i+c+l+d+m+e+j+f+j+g+j+h+k))
        forecast.close()
        counter += 1
    forecast.close()
                        
    
                        
def incrementCounter():
    counter = pickle.load(open('counter','rb'))
    counter += 1
    pickle.dump(counter,open('counter','wb'))
    return counter

def readCounter():
    return pickle.load(open('counter','rb'))

def is_ready_for_model(counter_read, min_hours):
    if counter_read>= min_hours*4*num_of_feathers and counter_read%(6*2)==0:
        return True
    else:
        return False

def run_model():
    os.system('sudo python EniaqSensorModel.py')

def collectSensorData():
    # Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
    ble.clear_cached_data()

    # Get the first available BLE network adapter and make sure it's powered on.
    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))

    # Disconnect any currently connected UART devices.  Good for cleaning up and
    # starting from a fresh state.
    print('Disconnecting any connected UART devices...')
    UART.disconnect_devices()

    # Scan for UART devices.
    print('Searching for UART devices...')
    try:
        adapter.start_scan()
        # Search for the first UART device found (will time out after 60 seconds
        # but you can specify an optional timeout_sec parameter to change it).

        #find all sensing devices
        devices = set()
        
        for i in range(10):
            found = set(UART.find_devices())
            #remove non-bluefruit devices
            found_filtered = set(filter(lambda x: 'Bluefruit52' in x.name ,found))
            #found_filtered = found
            new = found_filtered - devices
            devices.update(new)
            sleep(1)

        print("Found the following devices:")
        for device in devices:
            print(device.name,device.id)
        
	
        if devices is None:
            raise RuntimeError('Failed to find UART device!')
    except:
        adapter.stop_scan()
        return False
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()

    #collect sensor data every dt interval
    for device in devices:
        print('Connecting to device:',device.id)
        device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
                          # to change the timeout.
        
        # Once connected do everything else in a try/finally to make sure the device
        # is disconnected when done.
        try:
            # Wait for service discovery to complete for the UART service.  Will
            # time out after 60 seconds (specify timeout_sec parameter to override).
            print('Discovering services...')
            UART.discover(device)

            # Once service discovery is complete create an instance of the service
            # and start interacting with it.
            uart = UART(device)

            # Now wait up to one minute to receive data from the device.
            print('Waiting up to 60 seconds to receive data from the device...')
            received = uart.read(timeout_sec=60)
            if received is not None:
                # Received data, print it out.
                with open('sensordata','a') as sd:
                    sd.write(strftime("%Y-%m-%d %H:%M:%S ") + received + '\n')

                incrementCounter()
                counter_read = readCounter()
                min_hours = 72
                forecast_hours = 24
                if is_ready_for_model(counter_read, min_hours):
                    get_1day_forecast(forecast_hours)
                    run_model()
                get_current_conditions()
                print('Number of data points: '+ counter_read)
                print('Received: {0}'.format(received))
                print(strftime("%Y-%m-%d %H:%M:%S "))
                uart.write('good')
                print('Sent good')
            else:
                # Timeout waiting for data, None is returned.
                
                print('Received no data!')
        except:
            device.disconnect()
            return False
        finally:
            print('done')
            # Make sure device is disconnected on exit.
            device.disconnect()

    return True

    

# Main function implements the program logic so it can run in a background
# thread.  Most platforms require the main thread to handle GUI events and other
# asyncronous events like BLE actions.  All of the threading logic is taken care
# of automatically though and you just need to provide a main function that uses
# the BLE provider.      
def main():
    
    rt_delay = 5 #time delay in seconds before a retry
    #for i in range(10):
    
    #try to collect data 10 times and send warning
    #if it fails
    while True: 
    #for j in range(10):

        #stop trying if data is collected successfully
        failed = False
        try:
            collectSensorData()
        except Exception as e:
            print('It failed with error',e)
            print('retrying...')
            failed = True
        finally:
            break
            
        if not failed:
            break
        sleep(rt_delay)#wait rt_delay seconds to retry  




# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)
