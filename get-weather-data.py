from weatherdata_utils import WeatherStation
import datetime as dt
from time import sleep
from pytz import reference
from email.utils import parsedate_to_datetime


station_urls = ["http://w1.weather.gov/xml/current_obs/KNYC.xml",#Central Park
                "http://w1.weather.gov/xml/current_obs/KLGA.xml",#La Guardia Airport
                "http://w1.weather.gov/xml/current_obs/KJRB.xml",#Downtown Manhattan
                "http://w1.weather.gov/xml/current_obs/KJFK.xml"]#JFK Airport


stations = [WeatherStation(station_url) for station_url in station_urls]

    
#poll station every 15 minutes
while True:
    #or write to file instead
    with open('weatherdata','a') as wd:
        
        for st in stations:

            #check for the most recent measssurement
            if st.update():
                
                print('station',st.ID(),'was updated')

                wd.write('{0},{1},{2},{3},{4}\n'.format(st.time(),st.ID(),st.temp(),
                                                            st.humidity(),st.pressure()))
    
    print('going to sleep ..')
    sleep(15*60)
    

