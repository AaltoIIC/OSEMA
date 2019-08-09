from .models import User, Sensor, Type_of_sensor, Value_pair, Sensitivity, Sample_rate, Sensor, Wlan, Nb_iot, HTTP, HTTPS, Update, Variable
from sensor_management_platform.settings import FAILURE, BASE_DIR
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
    f = open(BASE_DIR + "/management/sensor_updates/" + filename, "w")
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
    if protocol_object.__class__.__name__ == "HTTPS":
        f.write("import ssl\n")
    if protocol_object.__class__.__name__ == "MQTT":
        f.write("from ubinascii import hexlify\n")

def write_libraries(f, communication_object, protocol_object):
    if protocol_object.__class__.__name__ == "MQTT":
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/mqtt.py") #MQTT library

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

    # write settings from sensor object
    f.write("DATA_SEND_RATE_S = {}\n".format(sensor_object.data_send_rate))
    f.write("BURST_LENGTH = {}\n".format(sensor_object.burst_length))
    f.write("BURST_RATE = {}\n".format(sensor_object.burst_rate))
    f.write("UPDATE_CHECK_LIMIT = {}\n".format(sensor_object.update_check_limit))
    f.write("UPDATE_URL = '{}'\n".format(sensor_object.update_url))
    f.write("UPDATE_PORT = {}\n".format(sensor_object.update_port))
    f.write("VARIABLE_NAMES = [")
    for o in Variable.objects.filter(sensor=sensor_object):
        f.write("'" + o.name + "'" + ",")
    f.write("]\n")

    # write setting from type of sensor object
    f.write("ADDRESS = {}\n".format(type_of_sensor_object.address))

    # write settings from sample rate
    f.write("SAMPLE_RATE_HZ = {}\n".format(sample_rate_object.sample_rate))
    f.write("BAUDRATE = {}\n".format(sample_rate_object.baudrate))

    if sensitivity_object.format_string == "": #Sensitivity object overrides samplerate's format string
        f.write("FORMAT_STRING = '{}'\n".format(sample_rate_object.format_string))

    # write settings from sensitivity_object
    if sensitivity_object.format_string != "":
        f.write("FORMAT_STRING = '{}'\n".format(sensitivity_object.format_string))

    # write settings from communication_object
    if communication_object.__class__.__name__ == "Wlan":
        ssid = communication_object.ssid
        security = communication_object.security
        key = communication_object.key
        if security == "WLAN.WPA2_ENT":
            username = communication_object.username
            f.write("NETWORK_SETTINGS = ['{}', ({}, '{}', '{}'), 'Pycom{}']\n".format(ssid, security, username, key, sensor_object.sensor_id))
        else:
            f.write("NETWORK_SETTINGS = ['{}', ({}, '{}'), 'Pycom{}']\n".format(ssid, security, key, sensor_object.sensor_id))

    # write setting from protocol_object
    if protocol_object.__class__.__name__ == "HTTP":
        f.write("DATA_SERVER_URL = '{}'\n".format(protocol_object.data_server_url))
        f.write("DATA_SERVER_PORT = {}\n".format(protocol_object.data_server_port))
        f.write("PATH = '{}'\n".format(protocol_object.path))
    elif protocol_object.__class__.__name__ == "HTTPS":
        f.write("DATA_SERVER_URL = '{}'\n".format(protocol_object.data_server_url))
        f.write("DATA_SERVER_PORT = {}\n".format(protocol_object.data_server_port))
        f.write("PATH = '{}'\n".format(protocol_object.path))
    elif protocol_object.__class__.__name__ == "MQTT":
        f.write("USER = '{}'\n".format(protocol_object.user))
        f.write("KEY = '{}'\n".format(protocol_object.key))
        f.write("TOPIC = '{}'\n".format(protocol_object.topic))
        f.write("BROKER_URL = '{}'\n".format(protocol_object.broker_url))
        f.write("BROKER_PORT = {}\n".format(protocol_object.broker_port))



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

def write_functions_always_needed(f):
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/send_error_msg.py") #send error message to the UI
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/calculate_length.py") #calculate length
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/config_sensor.py") #config sensor
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/read_data.py")#read data
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/read_values.py")#read values
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/sender.py")#sender
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/sync_rtc.py")#sync_rtc
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/check_update.py")#update check
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/convert_to_epoch.py")#helper function to convert date tuple to epoch

def write_optional_functions(f, sensor_object, communication_object, protocol_object):
    #If data needs to be handled spceifically (for example shifting bits)
    if sensor_object.model.handle_data_function:
        write_file_contents(f, sensor_object.model.handle_data_function.name)
        if sensor_object.data_format.name == "JSON":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_JSON_handle_data.py")
        elif sensor_object.data_format.name == "raw":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_raw_handle_data.py")
        elif sensor_object.data_format.name == "Regatta" and protocol_object.__class__.__name__ == "HTTP":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_Regatta_handle_data_HTTP.py")
    else:
        if sensor_object.data_format.name == "JSON":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_JSON.py")
        elif sensor_object.data_format.name == "raw":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_raw.py")
        elif sensor_object.data_format.name == "Regatta" and protocol_object.__class__.__name__ == "HTTP":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_Regatta_HTTP.py")

    #Write connect network
    if communication_object.__class__.__name__ == "Wlan":
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/connect_network_wlan.py")

    #Write close network
    if communication_object.__class__.__name__ == "Wlan":
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/close_network_wlan.py")

    #Write create and connect socket
    if protocol_object.__class__.__name__ == "HTTP":
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/create_and_connect_socket.py")
    elif protocol_object.__class__.__name__ == "HTTPS":
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/create_and_connect_socket_ssl.py")
    elif protocol_object.__class__.__name__ == "MQTT":
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/create_and_connect_socket.py")

    #Write keep connection if NOT data_send_rate > Wlan.close_limit
    if sensor_object.data_send_rate < sensor_object.network_close_limit:
        if communication_object.__class__.__name__ == "Wlan":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/keep_connection_wlan.py")

    if protocol_object.__class__.__name__ == "HTTP":
        if sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0: #Always close connection with HTTP
            if sensor_object.data_format.name == "JSON":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_connection/HTTP_JSON.py")
            elif sensor_object.data_format.name == "raw":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_connection/HTTP_raw.py")
            elif sensor_object.data_format.name == "Regatta":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_connection/HTTP_Regatta.py")
        elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit: #close connection
            if sensor_object.data_format.name == "JSON":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_connection/HTTP_JSON.py")
            elif sensor_object.data_format.name == "raw":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_connection/HTTP_raw.py")
            elif sensor_object.data_format.name == "Regatta":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_connection/HTTP_Regatta.py")
        elif sensor_object.data_send_rate > sensor_object.network_close_limit: #close network
            if sensor_object.data_format.name == "JSON":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_network/HTTP_JSON.py")
            elif sensor_object.data_format.name == "raw":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_network/HTTP_raw.py")
            elif sensor_object.data_format.name == "Regatta":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_network/HTTP_Regatta.py")
    elif protocol_object.__class__.__name__ == "HTTPS":
        pass
    elif protocol_object.__class__.__name__ == "MQTT":
        if sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0: #keep coonection
            if sensor_object.data_format.name == "JSON":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/keep_connection/MQTT_JSON.py")
            elif sensor_object.data_format.name == "raw":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/keep_connection/MQTT_raw.py")
            elif sensor_object.data_format.name == "Regatta" and sensor_object.model.handle_data_function:
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/keep_connection/MQTT_Regatta_handle_data.py")
            elif sensor_object.data_format.name == "Regatta":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/keep_connection/MQTT_Regatta.py")
        elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit: #close connection
            if sensor_object.data_format.name == "JSON":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_connection/MQTT_JSON.py")
            elif sensor_object.data_format.name == "raw":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_connection/MQTT_raw.py")
            elif sensor_object.data_format.name == "Regatta" and sensor_object.model.handle_data_function:
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_connection/MQTT_Regatta_handle_data.py")
            elif sensor_object.data_format.name == "Regatta":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_connection/MQTT_Regatta.py")
        elif sensor_object.data_send_rate > sensor_object.network_close_limit: #close network
            if sensor_object.data_format.name == "JSON":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_network/MQTT_JSON.py")
            elif sensor_object.data_format.name == "raw":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_network/MQTT_raw.py")
            elif sensor_object.data_format.name == "Regatta" and sensor_object.model.handle_data_function:
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_network/MQTT_Regatta_handle_data.py")
            elif sensor_object.data_format.name == "Regatta":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_network/MQTT_Regatta.py")
    else:
        print("There's an error with protocol class.")

    if protocol_object.__class__.__name__ == "HTTP":
        if sensor_object.burst_length > 0: #burst
            if sensor_object.data_send_rate == 0: #continuous sending
                if sensor_object.data_format.name == "JSON":
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/burst/HTTP_JSON.py")
                elif sensor_object.data_format.name == "raw":
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/burst/HTTP_raw.py")
                elif sensor_object.data_format.name == "Regatta":
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/burst/HTTP_Regatta.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0: #Always close connection with HTTP
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_close_connection_burst.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit: #close connection
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_close_connection_burst.py")
            elif sensor_object.data_send_rate > sensor_object.network_close_limit: #close network
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_close_network_burst.py")
        else: #not burst
            if sensor_object.data_send_rate == 0: #measure_continuous
                if sensor_object.data_format.name == "JSON":
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/HTTP_JSON.py")
                elif sensor_object.data_format.name == "raw":
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/HTTP_raw.py")
                elif sensor_object.data_format.name == "Regatta":
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/HTTP_Regatta.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0: #Always close connection with HTTP
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_close_connection.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit: #close connection
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_close_connection.py")
            elif sensor_object.data_send_rate > sensor_object.network_close_limit: #close network
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_close_network.py")
    elif protocol_object.__class__.__name__ == "MQTT":
        if sensor_object.burst_length > 0: #burst
            if sensor_object.data_send_rate == 0: #measure continuous
                if sensor_object.data_format.name == "JSON":
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/burst/MQTT_JSON.py")
                elif sensor_object.data_format.name == "raw":
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/burst/MQTT_raw.py")
                elif sensor_object.data_format.name == "Regatta" and sensor_object.model.handle_data_function:
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/burst/MQTT_Regatta_handle_data.py")
                elif sensor_object.data_format.name == "Regatta":
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/burst/MQTT_Regatta.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0: #keep connection
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_keep_connection/burst/MQTT.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit: #close connection
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_close_connection_burst.py")
            elif sensor_object.data_send_rate > sensor_object.network_close_limit: #close network
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_close_network_burst.py")
        else: #not burst
            if sensor_object.data_send_rate == 0: #measure continuous
                if sensor_object.data_format.name == "JSON":
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/MQTT_JSON.py")
                elif sensor_object.data_format.name == "raw":
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/MQTT_raw.py")
                elif sensor_object.data_format.name == "Regatta" and sensor_object.model.handle_data_function:
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/MQTT_Regatta_handle_data.py")
                elif sensor_object.data_format.name == "Regatta":
                    write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_continuous/MQTT_Regatta.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0: #keep connection
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_keep_connection/MQTT.py")
            elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit: #close connection
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_close_connection.py")
            elif sensor_object.data_send_rate > sensor_object.network_close_limit: #close network
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/measure_close_network.py")

    #Write ask_updates
    if sensor_object.data_send_rate > sensor_object.network_close_limit:
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/ask_updates_network_off.py")
    else:
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/ask_updates_network_on.py")

    #Write main
    if sensor_object.data_send_rate > sensor_object.network_close_limit:
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/main_no_network.py")
    else:
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/main_create_network.py")


def update_sensor(sensor_object):
    filename = generate_file(sensor_object)
    update = Update.objects.create(filename=filename, sensor=sensor_object)

def create_new_sensor(sensor_object):
    filename = generate_file(sensor_object)
    update = Update.objects.create(filename=filename, sensor=sensor_object)
    sensor_object.status = Sensor.WAITING_FOR_UPDATE

#Parse date from string and return datetime object
#Time string is in form: '2018-09-03 10:40:37.302390+0000'
def parse_date(date_string):
    format = "%Y-%m-%d %H:%M:%S.%f%z"
    try:
        return datetime.datetime.strptime(date_string, format)
    except:
        return "No date available"
