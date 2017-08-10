from urllib2 import urlopen
from urllib import urlencode
import json
from datetime import datetime as dt,tzinfo,timedelta



class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)

utc = UTC()



class ECWConnection():
    def __init__(self,host):
        self.__host__ = host

    #send data to server
    def sendData(self,sensorId,datetime,temp,hum,press):
        params   = urlencode({'temp':temp,'hum':hum,'press':press,'datetime':datetime,'sensorId':sensorId})
        response = urlopen('%s/newentry/insert?%s' % (self.__host__,params))
        return json.load(response)
    
    #prediction: json string of the form {'timestamp':temperature_value, ... }
    def updatePrediction(self,prediction):
        params   = urlencode({'prediction':prediction})
        response = urlopen('%s/newentry/insertPrediction?%s' % (self.__host__,params))
        return json.load(response)
    
    def getLatest(self):
        response = urlopen('%s/getreport/' % self.__host__)
        return json.load(response)