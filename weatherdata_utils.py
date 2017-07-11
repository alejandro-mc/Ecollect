import urllib.request as http
import xml.etree.ElementTree as ET
import datetime as dt
from email.utils import parsedate_to_datetime

class WeatherStation:
    '''Handles connection to weather station feed
    and extraction of temperature,pressure and humidity from raw response'''
    def __init__(self,url):
        self.__id__          = None
        self.__timeupdated__ = dt.datetime(1960,1,1,tzinfo=dt.timezone.utc)#initialized to a date in the past
        self.__temp__        = None
        self.__pressure__    = None
        self.__humidity__    = None
        self.__url__         = url
        self.raw=""
    
    def update(self):
        #get raw data from url
        rawtxt = http.urlopen(self.__url__).read()
        self.raw = rawtxt
        
        #parse xml to get data 
        (ID,
         temp,
         pressure,
         humidity,
         timeupdated)= newData = self.__parse__(rawtxt)
        
        #update if the data is new
        if timeupdated > self.__timeupdated__:
            (self.__id__,
             self.__temp__,
             self.__pressure__,
             self.__humidity__,
             self.__timeupdated__) = newData
            
            return True
        else:
            return False
    
    def __parse__(self,raw):
        tree = ET.fromstring(raw)
        
        str_id                = [i for i in tree.find('station_id').itertext()     ][0]
        str_temp_f            = [i for i in tree.find('temp_f').itertext()         ][0]
        str_pressure_mb       = [i for i in tree.find('pressure_mb').itertext()    ][0]
        str_relative_humidity = [i for i in tree.find('relative_humidity').itertext()][0]
        str_time              = [i for i in tree.find('observation_time_rfc822').itertext()][0]
        
        return (str_id,
                float(str_temp_f           ),
                float(str_pressure_mb      ),
                float(str_relative_humidity),
                parsedate_to_datetime(str_time))
    
    def ID(self):
        return self.__id__
    
    def temp(self):
        return self.__temp__
    
    def pressure(self):
        return self.__pressure__
    
    def humidity(self):
        return self.__humidity__
    def time(self):
        return self.__timeupdated__