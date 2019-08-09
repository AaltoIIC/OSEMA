import utime
import ustruct
import machine
from network import WLAN
import socket

INTERVAL = 5
MAXLINE = 1024
PATH = "get_update"
SOFTWARE_VERSION = "None"
"""Fill these. Go to browse sensors and select Info next to the new sensor."""
SENSOR_ID = #Fill this. For example: 45
SENSOR_KEY = #Fill this. For example: "mgpZrljj5wO0eVz8OhMT"
UPDATE_CHECK_IP_ADDRESS = #Fill this. For example "86.50.143.154:8000"
SSID = #Fill this. Wifi name. For example: "mywifi"
AUTH = #Fill this. For example: (WLAN.WPA2, "key") See: https://docs.pycom.io/firmwareapi/pycom/network/wlan#wlan-connect-ssid-auth-none-bssid-none-timeout-none-ca_certs-none-keyfile-none-certfile-none-identity-none
"""REMEMBER TO USE QUOTATION MARKS with SENSOR_KEY, UPDATE_SERVER_HOST AND SSID"""

"""PROGRAM BEGINS. DON'T CHANGE ANYTHING"""
HOST, PORT = [item.strip() for item in UPDATE_CHECK_IP_ADDRESS.split(":")]
PORT = int(PORT)


"""Connect to wifi"""
def connect_network():
    ssid, auth = SSID, AUTH
    wlan = WLAN(mode=WLAN.STA)
    wlan.connect(ssid=ssid, auth=auth)
    while not wlan.isconnected():
        pass
    print("wifi is connected")
    return wlan

def write_new_main(ip_address, port):
    addr = socket.getaddrinfo(ip_address, int(port))[0][-1]
    s = socket.socket()
    s.connect(addr)
    content_length = len("sensor_id={}&sensor_key={}&software_version={}".format(SENSOR_ID, SENSOR_KEY, SOFTWARE_VERSION))
    string = """POST /get_update HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\nsensor_id={}&sensor_key={}&software_version={}\r\n\r\n""".format(ip_address, content_length, SENSOR_ID, SENSOR_KEY, SOFTWARE_VERSION)
    s.send(bytes(string, 'utf8'))
    data_read = b""
    while True:
        data = s.recv(MAXLINE)
        if data:
            data_read += data
        else:
            break
    s.close()
    decoded_data = data_read.decode('ascii')
    print(decoded_data)
    payload_begins = decoded_data.find("import") #Payload string always begins with an import statement
    if payload_begins == -1:
        if decoded_data.find("UP-TO-DATE") != -1:
            print("Software up-to-date")
            return
        else:
            print("There's an error with the server response")
    else:
        print("else")
        data = decoded_data[payload_begins:]
        f = open("new_main.txt", "w")
        f.write(data)
        f.close()
        print("Writing data succeed!")
        #Confirm that data is received
        s = socket.socket()
        s.connect(addr)
        content_length = len("sensor_id={}&sensor_key={}".format(SENSOR_ID, SENSOR_KEY))
        confirmation = """POST /confirm_update HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\nsensor_id={}&sensor_key={}\r\n\r\n""".format(ip_address, content_length, SENSOR_ID, SENSOR_KEY)
        p = s.send(bytes(confirmation, 'utf8'))
        s.close()
        print("update confirmed")
        utime.sleep(1)
        machine.reset()


def ask_updates(interval, ip_address, port):
    while True:
        write_new_main(ip_address, port)
        utime.sleep(interval)

def main():
    connect_network()
    ask_updates(INTERVAL, HOST, PORT)

main()
