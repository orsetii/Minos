import network
import time
import socket
import urequests
import ujson

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
    r = urequests.get("http://192.168.0.135:8080/temperature/internal")
    return r.content

def get_external_temp():   
    r = urequests.get("http://192.168.0.135:8080/temperature/external")
    return r.content


def register(name):
    post_data = ujson.dumps({ 'name': name})
    request_url = 'http://192.168.0.135:8080/hive/register'
    res = urequests.post(request_url, headers = {'content-type': 'application/json'}, data = post_data)
    
def hive_status():
    r = urequests.get("http://192.168.0.135:8080/hive")
    return r.content

def get_time():
    r = urequests.get("http://192.168.0.135:8080/time")
    return r.content

def get_time_no_seconds():
    r = urequests.get("http://192.168.0.135:8080/time/no_seconds")
    return r.content

def get_date():
    r = urequests.get("http://192.168.0.135:8080/time/date")
    return r.content
    

    