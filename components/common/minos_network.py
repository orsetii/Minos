import network
import time
import socket
import urequests
import ujson
from micropython import const

API_URL = const("http://192.168.0.135:8080")

def connect():
    ssid = "VM8691605"
    password = "Jf7gsctxwYmf"

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect (ssid, password)

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
 
def get_internal_temp():
    r = urequests.get(API_URL + "/temperature/internal")
    return r.content

def get_external_temp():   
    r = urequests.get(API_URL + "/temperature/external")
    return r.content


def register(name):
    post_data = ujson.dumps({ 'name': name})
    request_url = API_URL + '/hive/register'
    res = urequests.post(request_url, headers = {'content-type': 'application/json'}, data = post_data)
    
def hive_status():
    r = urequests.get(API_URL + "/hive")
    return r.content

def get_time():
    r = urequests.get(API_URL + "/time")
    return r.content

def get_time_no_seconds():
    r = urequests.get(API_URL + "/time/no_seconds")
    return r.content

def get_date():
    r = urequests.get(API_URL + "/time/date")
    return r.content

def post_temp_and_humidity(temp, humidity, external):
    url = API_URL + "/temperature/"
    if external is True:        
        url + "external"
    else:
        url + "internal"
        
    post_data = ujson.dumps({ 'temperature': temp, 'humidity' : humidity })
    r = urequests.post(url, headers = {'content-type': 'application/json'}, data = post_data)
    return r.content
    

    