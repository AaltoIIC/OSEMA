from .models import User, Sensor, Type_of_sensor, Value_pair, Sensitivity, Sample_rate, Sensor, Wlan, Nb_iot, Http, Https, Update
from sensor_management_platform.settings import FAILURE
from requests.auth import HTTPBasicAuth
import datetime
import requests
import json

import time
import os

"""Update clock from internet"""
def update_time():
    #from https://stackoverflow.com/questions/5222951/easy-way-to-get-the-correct-time-in-python
    try:
        import ntplib
        client = ntplib.NTPClient()
        response = client.request('0.fi.pool.ntp.org')
        os.system('date ' + time.strftime('%m%d%H%M%Y.%S',time.localtime(response.tx_time)))
    except:
        print('Could not sync with time server.')

"""Write contents of filename to file f"""
def write_file_contents(f, filename):
    r = open(filename, "r")
    for row in r:
        f.write(row)
    r.close()

"""Generate file to PyCom board"""
def generate_file(sensor_object):
    time_string = time.strftime("%Y_%m_%d_%H_%M_%S")
    filename = str(sensor_object.sensor_id) + "_" + time_string + ".txt"
    f = open("management/sensor_updates/" + filename, "w")
    type_of_sensor_object = sensor_object.model
    sample_rate_object = sensor_object.sample_rate
    sensitivity_object = sensor_object.sensitivity
    communication_object = sensor_object.communication_object
    protocol_object = sensor_object.protocol_object
    write_imports(f, communication_object, protocol_object)
    write_libraries(f, communication_object, protocol_object)
    write_global(f, sensor_object, type_of_sensor_object, sample_rate_object, sensitivity_object, communication_object, protocol_object, filename)
    #write_functions_used_by_functions_always_needed(f, sensor_object, protocol_object)
    write_functions_always_needed(f)
    write_optional_functions(f, sensor_object, communication_object, protocol_object)
    f.write("main()\n")
    f.close()
    return filename


def write_imports(f, communication_object, protocol_object):
    f.write("import gc\n")
    f.write("import pycom\n")
    f.write("import socket\n")
    f.write("import micropython\n")
    f.write("import utime\n")
    f.write("import machine\n")
    f.write("import _thread\n")
    f.write("import ustruct\n")
    f.write("import uos\n")
    f.write("from machine import RTC, I2C, Timer\n")
    if communication_object.__class__.__name__ == "Wlan":
        f.write("from network import WLAN\n")
    if protocol_object.__class__.__name__ == "Https":
        f.write("import ssl\n")
    if protocol_object.__class__.__name__ == "MQTT":
        f.write("from ubinascii import hexlify\n")

def write_libraries(f, communication_object, protocol_object):
    if protocol_object.__class__.__name__ == "MQTT":
        write_file_contents(f, "management/pycom_functions/mqtt.py") #MQTT library

def write_global(f, sensor_object, type_of_sensor_object, sample_rate_object, sensitivity_object, communication_object, protocol_object, filename):
    write_settings(f, sensor_object, type_of_sensor_object, sample_rate_object, sensitivity_object, communication_object, protocol_object, filename)
    write_read(f, sample_rate_object, sensitivity_object)
    write_write(f, sample_rate_object, sensitivity_object)

def write_settings(f, sensor_object, type_of_sensor_object, sample_rate_object, sensitivity_object, communication_object, protocol_object, filename):
    #These are always needed
    f.write("CONNECTION_BROKEN = -1\n")
    f.write("MAXLINE = 1024 #maximum number of bytes read with one recv command\n")
    f.write("FAILURE = -1\n")
    f.write("SUCCESS = 1\n")
    f.write("SENSOR_ID = {}\n".format(sensor_object.sensor_id))
    f.write("SENSOR_KEY = '{}'\n".format(sensor_object.sensor_key))
    f.write("SOFTWARE_VERSION = '{}'\n".format(filename))
    f.write("SETTINGS_DICT = {}\n")

    # write settings from sensor object
    f.write("SETTINGS_DICT['DATA_SEND_RATE_S'] = {}\n".format(sensor_object.data_send_rate))
    f.write("SETTINGS_DICT['BURST_LENGTH'] = {}\n".format(sensor_object.burst_length))
    f.write("SETTINGS_DICT['BURST_RATE'] = {}\n".format(sensor_object.burst_rate))
    f.write("SETTINGS_DICT['UPDATE_CHECK_LIMIT'] = {}\n".format(sensor_object.update_check_limit))
    f.write("SETTINGS_DICT['UPDATE_IP_ADDRESS'] = '{}'\n".format(sensor_object.update_check_ip_address))
    f.write("SETTINGS_DICT['IP_ADDRESS_SEND'] = '{}'\n".format(sensor_object.data_server_ip_address))

    # write setting from type of sensor object
    f.write("SETTINGS_DICT['ADDRESS'] = {}\n".format(type_of_sensor_object.address))

    # write settings from sample rate
    f.write("SETTINGS_DICT['SAMPLE_RATE_HZ'] = {}\n".format(sample_rate_object.sample_rate))
    f.write("SETTINGS_DICT['BAUDRATE'] = {}\n".format(sample_rate_object.baudrate))

    if sensitivity_object.format_string == "": #Sensitivity object overrides samplerate's format string
        f.write("SETTINGS_DICT['FORMAT_STRING'] = '{}'\n".format(sample_rate_object.format_string))

    # write settings from sensitivity_object
    if sensitivity_object.format_string != "":
        f.write("SETTINGS_DICT['FORMAT_STRING'] = {}\n".format(sensitivity_object.format_string))

    # write settings from communication_object
    if communication_object.__class__.__name__ == "Wlan":
        ssid = communication_object.ssid
        security = communication_object.security
        key = communication_object.key
        if security == "WLAN.WPA2_ENT":
            username = communication_object.username
            f.write("SETTINGS_DICT['NETWORK_SETTINGS'] = ['{}', ({}, '{}', '{}'), 'Pycom{}']\n".format(ssid, security, username, key, sensor_object.sensor_id))
        else:
            f.write("SETTINGS_DICT['NETWORK_SETTINGS'] = ['{}', ({}, '{}'), 'Pycom{}']\n".format(ssid, security, key, sensor_object.sensor_id))

    # write setting from protocol_object
    if protocol_object.__class__.__name__ == "Http":
        f.write("SETTINGS_DICT['PATH'] = '{}'\n".format(protocol_object.path))
    elif protocol_object.__class__.__name__ == "Https":
        f.write("SETTINGS_DICT['PATH'] = '{}'\n".format(protocol_object.path))
    elif protocol_object.__class__.__name__ == "MQTT":
        f.write("SETTINGS_DICT['USER'] = '{}'\n".format(protocol_object.user))
        f.write("SETTINGS_DICT['KEY'] = '{}'\n".format(protocol_object.key))
        f.write("SETTINGS_DICT['TOPIC'] = '{}'\n".format(protocol_object.topic))
        f.write("SETTINGS_DICT['DATA_SERVER_URL'] = '{}'\n".format(protocol_object.data_server_url))
        f.write("SETTINGS_DICT['PORT'] = {}\n".format(protocol_object.port))



def write_read(f, sample_rate_object, sensitivity_object):
    f.write("READ_DICT = {}\n")
    for object in sample_rate_object.read_values.all():
        f.write("READ_DICT['{}'] = {}\n".format(object.value1, object.value2))
    for object in sensitivity_object.read_values.all():
        f.write("READ_DICT['{}'] = {}\n".format(object.value1, object.value2))

def write_write(f, sample_rate_object, sensitivity_object):
    f.write("WRITE_DICT = {}\n")
    for object in sample_rate_object.write_values.all():
        f.write("WRITE_DICT['{}'] = {}\n".format(object.value1, object.value2))
    for object in sensitivity_object.write_values.all():
        f.write("WRITE_DICT['{}'] = {}\n".format(object.value1, object.value2))

"""
def write_functions_used_by_functions_always_needed(f, sensor_object, protocol_object):
    if protocol_object.__class__.__name__ == "Http":
        pass #update when needed
    elif protocol_object.__class__.__name__ == "Https":
        pass #update when needed
"""

def write_functions_always_needed(f):
    write_file_contents(f, "management/pycom_functions/in_every_program/send_error_msg.py") #send error message to the UI
    write_file_contents(f, "management/pycom_functions/in_every_program/calculate_length.py") #calculate length
    write_file_contents(f, "management/pycom_functions/in_every_program/config_sensor.py") #config sensor
    write_file_contents(f, "management/pycom_functions/in_every_program/read_data.py")#read data
    write_file_contents(f, "management/pycom_functions/in_every_program/read_values.py")#read values
    write_file_contents(f, "management/pycom_functions/in_every_program/sender.py")#sender
    write_file_contents(f, "management/pycom_functions/in_every_program/sync_rtc.py")#sync_rtc
    write_file_contents(f, "management/pycom_functions/in_every_program/write_new_main.py")#write new main

def write_optional_functions(f, sensor_object, communication_object, protocol_object):
    #If data needs to be handled spceifically (for example shifting bits)
    if sensor_object.model.handle_data_function:
        write_file_contents(f, "management/pycom_functions/send_data_handle.py")#send data
        write_file_contents(f, sensor_object.model.handle_data_function.name)
    else:
        write_file_contents(f, "management/pycom_functions/send_data.py")#send data


    #Write connect network
    if communication_object.__class__.__name__ == "Wlan":
        write_file_contents(f, "management/pycom_functions/connect_network_wlan.py")

    #Write close network
    if communication_object.__class__.__name__ == "Wlan":
        write_file_contents(f, "management/pycom_functions/close_network_wlan.py")

    #Write create and connect socket
    if protocol_object.__class__.__name__ == "Http":
        write_file_contents(f, "management/pycom_functions/create_and_connect_socket.py")
    elif protocol_object.__class__.__name__ == "Https":
        write_file_contents(f, "management/pycom_functions/create_and_connect_socket_ssl.py")
    elif protocol_object.__class__.__name__ == "LWDTP":
        write_file_contents(f, "management/pycom_functions/create_and_connect_socket.py")
    elif protocol_object.__class__.__name__ == "MQTT":
        write_file_contents(f, "management/pycom_functions/create_and_connect_socket.py")

    #Write keep connection if NOT data_send_rate > Wlan.close_limit
    if sensor_object.data_send_rate < sensor_object.network_close_limit:
        if communication_object.__class__.__name__ == "Wlan":
            write_file_contents(f, "management/pycom_functions/keep_connection_wlan.py")

    #Write communicate with server
    if protocol_object.__class__.__name__ == "LWDTP":
        if sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0:
            write_file_contents(f, "management/pycom_functions/communicate_with_server_keep_connection_LWDTP.py")
        elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit:
            write_file_contents(f, "management/pycom_functions/communicate_with_server_close_connection_LWDTP.py")
        elif sensor_object.data_send_rate > sensor_object.network_close_limit:
            write_file_contents(f, "management/pycom_functions/communicate_with_server_close_network_LWDTP.py")
    elif protocol_object.__class__.__name__ == "Http":
        if sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0:
            write_file_contents(f, "management/pycom_functions/communicate_with_server_close_connection_HTTP.py") #Always close connection
        elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit:
            write_file_contents(f, "management/pycom_functions/communicate_with_server_close_connection_HTTP.py")
        elif sensor_object.data_send_rate > sensor_object.network_close_limit:
            write_file_contents(f, "management/pycom_functions/communicate_with_server_close_network_HTTP.py")
    elif protocol_object.__class__.__name__ == "Https":
        pass
    elif protocol_object.__class__.__name__ == "MQTT":
        if sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0:
            write_file_contents(f, "management/pycom_functions/communicate_with_server_keep_connection_MQTT.py")
        elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit:
            write_file_contents(f, "management/pycom_functions/communicate_with_server_close_connection_MQTT.py")
        elif sensor_object.data_send_rate > sensor_object.network_close_limit:
            write_file_contents(f, "management/pycom_functions/communicate_with_server_close_network_MQTT.py")
    else:
        print("There's an error with protocol class.")

    #Write measurement
    if protocol_object.__class__.__name__ == "LWDTP":
        if sensor_object.burst_length > 0: #burst
            if sensor_object.data_send_rate == 0:
                write_file_contents(f, "management/pycom_functions/measure_continuous_burst_LWDTP.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0:
                write_file_contents(f, "management/pycom_functions/measure_keep_connection_burst_LWDTP.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit:
                write_file_contents(f, "management/pycom_functions/measure_close_connection_burst.py")
            elif sensor_object.data_send_rate > sensor_object.network_close_limit:
                write_file_contents(f, "management/pycom_functions/measure_close_network_burst.py")
        else: #not burst
            if sensor_object.data_send_rate == 0:
                write_file_contents(f, "management/pycom_functions/measure_continuous_LWDTP.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0:
                write_file_contents(f, "management/pycom_functions/measure_keep_connection_LWDTP.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit:
                write_file_contents(f, "management/pycom_functions/measure_close_connection.py")
            elif sensor_object.data_send_rate > sensor_object.network_close_limit:
                write_file_contents(f, "management/pycom_functions/measure_close_network.py")
    elif protocol_object.__class__.__name__ == "Http":
        if sensor_object.burst_length > 0: #burst
            if sensor_object.data_send_rate == 0:
                write_file_contents(f, "management/pycom_functions/measure_continuous_burst_HTTP.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0:
                write_file_contents(f, "management/pycom_functions/measure_close_connection_burst.py") #Always close connection
            elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit:
                write_file_contents(f, "management/pycom_functions/measure_close_connection_burst.py")
            elif sensor_object.data_send_rate > sensor_object.network_close_limit:
                write_file_contents(f, "management/pycom_functions/measure_close_network_burst.py")
        else: #not burst
            if sensor_object.data_send_rate == 0:
                write_file_contents(f, "management/pycom_functions/measure_continuous_HTTP.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0:
                write_file_contents(f, "management/pycom_functions/measure_close_connection.py") #Always close connection
            elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit:
                write_file_contents(f, "management/pycom_functions/measure_close_connection.py")
            elif sensor_object.data_send_rate > sensor_object.network_close_limit:
                write_file_contents(f, "management/pycom_functions/measure_close_network.py")
    elif protocol_object.__class__.__name__ == "MQTT":
        if sensor_object.burst_length > 0: #burst
            if sensor_object.data_send_rate == 0:
                write_file_contents(f, "management/pycom_functions/measure_continuous_burst_MQTT.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0:
                write_file_contents(f, "management/pycom_functions/measure_keep_connection_burst_MQTT.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit:
                write_file_contents(f, "management/pycom_functions/measure_close_connection_burst.py")
            elif sensor_object.data_send_rate > sensor_object.network_close_limit:
                write_file_contents(f, "management/pycom_functions/measure_close_network_burst.py")
        else: #not burst
            if sensor_object.data_send_rate == 0:
                write_file_contents(f, "management/pycom_functions/measure_continuous_MQTT.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0:
                write_file_contents(f, "management/pycom_functions/measure_keep_connection_MQTT.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit:
                write_file_contents(f, "management/pycom_functions/measure_close_connection.py")
            elif sensor_object.data_send_rate > sensor_object.network_close_limit:
                write_file_contents(f, "management/pycom_functions/measure_close_network.py")


    #Write ask_updates
    if sensor_object.data_send_rate > sensor_object.network_close_limit:
        write_file_contents(f, "management/pycom_functions/ask_updates_network_off.py")
    else:
        write_file_contents(f, "management/pycom_functions/ask_updates_network_on.py")

    #Write main
    if sensor_object.data_send_rate > sensor_object.network_close_limit:
        write_file_contents(f, "management/pycom_functions/main_no_network.py")
    else:
        write_file_contents(f, "management/pycom_functions/main_create_network.py")





"""Communication with dataserver"""
def update_sensor_status(sensor_object, status):
    ip_address, port = sensor_object.data_server_ip_address.split(":")
    url = "http://" + ip_address + ":" + str(int(port) + 1) + "/api/v1.0/sensors/" + str(sensor_object.sensor_id) + "/"
    body = {"sensor_id": sensor_object.sensor_id,
            "status" : status}
    try:
        access_token = sensor_object.protocol_object.access_token
        make_put_request(url, access_token, body, sensor_object)
    except:
        return FAILURE


def send_update_to_data_server(sensor_object):
    ip_address, port = sensor_object.data_server_ip_address.split(":")
    url = "http://" + ip_address + ":" + str(int(port) + 1) + "/api/v1.0/sensors/" + str(sensor_object.sensor_id) + "/"
    body = {"sensor_id": sensor_object.sensor_id,
            "sensor_name": sensor_object.sensor_name,
            "update_ip_address": sensor_object.update_check_ip_address,
            "status" : sensor_object.status}
    try:
        access_token = sensor_object.protocol_object.access_token
        make_put_request(url, access_token, body, sensor_object)
    except:
        return FAILURE

def send_new_sensor_to_dataserver(sensor_object):
    ip_address, port = sensor_object.data_server_ip_address.split(":")
    url = "http://" + ip_address + ":" + str(int(port) + 1) + "/api/v1.0/sensors/"
    body = {"sensor_id": sensor_object.sensor_id,
            "sensor_name": sensor_object.sensor_name,
            "sensor_key": sensor_object.sensor_key,
            "update_ip_address": sensor_object.update_check_ip_address,
            "status" : sensor_object.status}
    try:
        access_token = sensor_object.protocol_object.access_token
        make_post_request(url, access_token, body, sensor_object)
    except:
        return FAILURE

def update_key(sensor_object):
    ip_address, port = sensor_object.data_server_ip_address.split(":")
    url = "http://" + ip_address + ":" + str(int(port) + 1) + "/api/v1.0/sensors/" + str(sensor_object.sensor_id) + "/"
    body = {"sensor_id": sensor_object.sensor_id,
            "sensor_key": sensor_object.sensor_key}
    try:
        access_token = sensor_object.protocol_object.access_token
        make_put_request(url, access_token, body, sensor_object)
    except:
        return FAILURE


def update_sensor(sensor_object):
    filename = generate_file(sensor_object)
    update = Update.objects.create(filename=filename, sensor=sensor_object)
    send_update_to_data_server(sensor_object)

def create_new_sensor_to_dataserver(sensor_object):
    filename = generate_file(sensor_object)
    update = Update.objects.create(filename=filename, sensor=sensor_object)
    sensor_object.status = Sensor.WAITING_FOR_UPDATE
    send_new_sensor_to_dataserver(sensor_object)

def delete_sensor_from_data_server(sensor_object):
    ip_address, port = sensor_object.data_server_ip_address.split(":")
    url = "http://" + ip_address + ":" + str(int(port) + 1) + "/api/v1.0/sensors/" + str(sensor_object.sensor_id) + "/"
    try:
        access_token = sensor_object.protocol_object.access_token
        return make_delete_request(url, access_token, sensor_object)
    except:
        return FAILURE

def get_latest_data_date(sensor_object):
    ip_address, port = sensor_object.data_server_ip_address.split(":")
    url = "http://" + ip_address + ":" + str(int(port) + 1) + "/api/v1.0/get_sensor_files/"
    try:
        access_token = sensor_object.protocol_object.access_token
        return make_get_request(url, access_token, sensor_object)
    except:
        return FAILURE

#Parse date from string and return datetime object
#Time string is in form: '2018-09-03 10:40:37.302390+0000'
def parse_date(date_string):
    format = "%Y-%m-%d %H:%M:%S.%f%z"
    try:
        return datetime.datetime.strptime(date_string, format)
    except:
        return "No date available"

def get_data_files(sensor_object):
    ip_address, port = sensor_object.data_server_ip_address.split(":")
    url = "http://" + ip_address + ":" + str(int(port) + 1) + "/api/v1.0/get_sensor_files/" + str(sensor_object.sensor_id)
    try:
        access_token = sensor_object.protocol_object.access_token
        return make_get_request(url, access_token, sensor_object)
    except:
        return FAILURE

def delete_datafile_from_data_server(datafile, sensor_object):
    ip_address, port = sensor_object.data_server_ip_address.split(":")
    url = "http://" + ip_address + ":" + str(int(port) + 1) + "/api/v1.0/datafiles/" + datafile + "/"
    try:
        access_token = sensor_object.protocol_object.access_token
        return make_delete_request(url, access_token, sensor_object)
    except:
        return FAILURE

def get_datafile(filename, sensor_object):
    ip_address, port = sensor_object.data_server_ip_address.split(":")
    url = "http://" + ip_address + ":" + str(int(port) + 1) + "/api/v1.0/get_datafile/" + filename
    try:
        access_token = sensor_object.protocol_object.access_token
        return make_get_request(url, access_token, sensor_object)
    except:
        return FAILURE

def get_date_and_type(filename, sensor_object):
    ip_address, port = sensor_object.data_server_ip_address.split(":")
    url = "http://" + ip_address + ":" + str(int(port) + 1) + "/api/v1.0/get_sensor_type_and_date/" + filename
    try:
        access_token = sensor_object.protocol_object.access_token
        return make_get_request(url, access_token, sensor_object)
    except:
        return FAILURE

def get_previous_and_next(filename, sensor_object):
    ip_address, port = sensor_object.data_server_ip_address.split(":")
    url = "http://" + ip_address + ":" + str(int(port) + 1) + "/api/v1.0/get_previous_and_next/" + str(sensor_object.sensor_id) + "/" + filename
    try:
        access_token = sensor_object.protocol_object.access_token
        return make_get_request(url, access_token, sensor_object)
    except:
        return FAILURE

def make_get_request(url, access_token, sensor_object):
    try:
        while True:
            header = {'Authorization': 'Bearer ' + str(access_token)}
            r = requests.get(url=url, headers=header, timeout=5)
            if 199 < r.status_code < 300:
                return r
            elif r.status_code == 401: #Old token
                access_token = get_new_token_from_data_server(sensor_object)
                if access_token == FAILURE:
                    print("Something went wrong!")
                    return FAILURE
                sensor_object.protocol_object.access_token = access_token
                sensor_object.protocol_object.save()
            else:
                print("Something went wrong!")
                return FAILURE
    except:
        print("Something went wrong!")
        return FAILURE

def make_delete_request(url, access_token, sensor_object):
    try:
        while True:
            header = {'Authorization': 'Bearer ' + str(access_token)}
            r = requests.delete(url=url, headers=header, timeout=5)
            if 199 < r.status_code < 300:
                return r
            elif r.status_code == 401: #Old token
                access_token = get_new_token_from_data_server(sensor_object)
                if access_token == FAILURE:
                    print("Something went wrong!")
                    return FAILURE
                sensor_object.protocol_object.access_token = access_token
                sensor_object.protocol_object.save()
            else:
                print("Something went wrong!")
                return FAILURE
    except:
        print("Something went wrong!")
        return FAILURE

def make_put_request(url, access_token, body, sensor_object):
    try:
        while True:
            header = {'Authorization': 'Bearer ' + str(access_token)}
            r = requests.put(url=url, data=body, headers=header, timeout=5)
            if 199 < r.status_code < 300:
                return r
            elif r.status_code == 401: #Old token
                access_token = get_new_token_from_data_server(sensor_object)
                if access_token == FAILURE:
                    print("Something went wrong!")
                    return FAILURE
                sensor_object.protocol_object.access_token = access_token
                sensor_object.protocol_object.save()
            else:
                print("Something went wrong!")
                return FAILURE
    except:
        print("Something went wrong!")
        return FAILURE

def make_post_request(url, access_token, body, sensor_object):
    try:
        while True:
            header = {'Authorization': 'Bearer ' + str(access_token)}
            r = requests.post(url=url, data=body, headers=header, timeout=5)
            if 199 < r.status_code < 300:
                return r
            elif r.status_code == 401: #Old token
                access_token = get_new_token_from_data_server(sensor_object)
                if access_token == FAILURE:
                    print("Something went wrong!")
                    return FAILURE
                sensor_object.protocol_object.access_token = access_token
                sensor_object.protocol_object.save()
            else:
                print("Something went wrong!")
                return FAILURE
    except:
        print("Something went wrong!")
        return FAILURE

def get_new_token_from_data_server(sensor_object):
    ip_address, port = sensor_object.data_server_ip_address.split(":")
    url = "http://" + ip_address + ":" + str(int(port) + 1) + "/api/v1.0/token/refresh/"
    body = {"refresh": sensor_object.protocol_object.refresh_token,
            }
    try:
        r = requests.post(url=url, data=body, timeout=5)
        if 199 < r.status_code < 300:
            data_as_dict = dict(r.json())
            return data_as_dict['access']
        else:
            print("Something went wrong!")
            return FAILURE
    except IndexError:
        print("Something went wrong!")
        return FAILURE
