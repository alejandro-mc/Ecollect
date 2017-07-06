#!/usr/bin/env python
# Example of interaction with a BLE UART device using a UART service
# implementation.
# Author: Tony DiCola
import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART
from time import sleep, strftime, time
import time

# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()


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
                
                print('Received: {0}'.format(received))
                print(strftime("%Y-%m-%d %H:%M:%S "))
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
