from .models import User, Sensor, Type_of_sensor, Value_pair, Sensitivity, Sample_rate, Sensor, Wlan, Nb_iot, HTTP, HTTPS, Update, Variable, Server
from sensor_management_platform.settings import FAILURE, BASE_DIR
from requests.auth import HTTPBasicAuth
import datetime
import requests
import json
from Crypto.Cipher import AES
import time
import os
import binascii
import hashlib
import hmac

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
    write_imports(f, sensor_object, communication_object, protocol_object)
    write_libraries(f, communication_object, protocol_object)
    write_global(f, sensor_object, type_of_sensor_object, sample_rate_object, sensitivity_object, communication_object, protocol_object, filename)
    #write_functions_used_by_functions_always_needed(f, sensor_object, protocol_object)
    write_functions_always_needed(f)
    write_optional_functions(f, sensor_object, communication_object, protocol_object)
    f.write("main()\n")
    f.close()
    return filename


def write_imports(f, sensor_object, communication_object, protocol_object):
    f.write("import gc\n")
    f.write("import uhashlib\n")
    f.write("import ubinascii\n")
    f.write("import pycom\n")
    f.write("import socket\n")
    f.write("import micropython\n")
    f.write("import utime\n")
    f.write("import machine\n")
    f.write("import _thread\n")
    f.write("import ustruct\n")
    f.write("import uos\n")
    f.write("from crypto import AES\n")
    f.write("import crypto\n")
    f.write("from machine import RTC, I2C, Timer\n")
    if communication_object.__class__.__name__ == "Wlan":
        f.write("from network import WLAN\n")
    if protocol_object.__class__.__name__ == "MQTT":
        f.write("from ubinascii import hexlify\n")
    if protocol_object.__class__.__name__ == "HTTPS" or sensor_object.update_https:
        f.write("import ssl\n")

def write_libraries(f, communication_object, protocol_object):
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/hmac.py") #hmac library
    if protocol_object.__class__.__name__ == "MQTT":
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/mqtt.py") #MQTT library

def write_global(f, sensor_object, type_of_sensor_object, sample_rate_object, sensitivity_object, communication_object, protocol_object, filename):
    write_settings(f, sensor_object, type_of_sensor_object, sample_rate_object, sensitivity_object, communication_object, protocol_object, filename)
    write_read(f, sample_rate_object, sensitivity_object)
    write_write(f, sample_rate_object, sensitivity_object)

def write_settings(f, sensor_object, type_of_sensor_object, sample_rate_object, sensitivity_object, communication_object, protocol_object, filename):
    #These are always needed
    f.write("CONNECTION_BROKEN = -1\n")
    f.write("FAILURE_MEM = 4\n")
    f.write("FAILURE_OS = 5\n")
    f.write("FAILURE_I2C = 6\n")
    f.write("MAXLINE = 1024 #maximum number of bytes read with one recv command\n")
    f.write("MAX_SOFTWARE_SIZE = 50000#bytes, prevents memory overflow \n")
    f.write("SENSOR_ID = {}\n".format(sensor_object.sensor_id))
    f.write("SENSOR_KEY = '{}'\n".format(sensor_object.sensor_key))
    f.write("SHARED_SECRET_UPDATES = '{}'\n".format(sensor_object.shared_secret_updates))
    f.write("SOFTWARE_VERSION = '{}'\n".format(filename))
    f.write("SERVER_KEY = '{}'\n".format(Server.objects.all()[0].server_key))

    # write settings from sensor object
    f.write("DATA_SEND_RATE_S = {}\n".format(sensor_object.data_send_rate))
    f.write("BURST_LENGTH = {}\n".format(sensor_object.burst_length))
    f.write("BURST_RATE = {}\n".format(sensor_object.burst_rate))
    f.write("UPDATE_CHECK_LIMIT = {}\n".format(sensor_object.update_check_limit))
    f.write("UPDATE_URL = '{}'\n".format(sensor_object.update_url))
    f.write("UPDATE_PORT = {}\n".format(sensor_object.update_port))
    f.write("UPDATE_HTTPS = {}\n".format(sensor_object.update_https))
    f.write("VARIABLE_NAMES = [")
    for o in Variable.objects.filter(sensor=sensor_object):
        f.write("'" + o.name + "'" + ",")
    f.write("]\n")

    # write setting from type of sensor object
    f.write("ADDRESS = {}\n".format(type_of_sensor_object.address))

    # If data is encrypted write encryption key
    if sensor_object.encrypt_data:
        f.write("SHARED_SECRET_DATA = '{}'\n".format(sensor_object.shared_secret_data))

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
        f.write("USE_SSL_DATA_SERVER = False\n")
    elif protocol_object.__class__.__name__ == "HTTPS":
        f.write("DATA_SERVER_URL = '{}'\n".format(protocol_object.data_server_url))
        f.write("DATA_SERVER_PORT = {}\n".format(protocol_object.data_server_port))
        f.write("PATH = '{}'\n".format(protocol_object.path))
        f.write("USE_SSL_DATA_SERVER = True\n")
    elif protocol_object.__class__.__name__ == "MQTT":
        f.write("USER = '{}'\n".format(protocol_object.user))
        f.write("KEY = '{}'\n".format(protocol_object.key))
        f.write("TOPIC = '{}'\n".format(protocol_object.topic))
        f.write("BROKER_URL = '{}'\n".format(protocol_object.broker_url))
        f.write("BROKER_PORT = {}\n".format(protocol_object.broker_port))
        f.write("USE_SSL_DATA_SERVER = False\n")



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
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/decrypt_msg.py") #decrypt messages
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/encrypt_msg.py") #encrypt messages
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/send_error_msg.py") #send error message to the UI
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/calculate_length.py") #calculate length
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/config_sensor.py") #config sensor
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/read_data.py")#read data
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/sender.py")#sender
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/sync_rtc.py")#sync_rtc
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/convert_to_epoch.py")#helper function to convert date tuple to epoch
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/create_and_connect_socket.py")#Write create and connect socket
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/measure_loop.py")#Write create and connect socket
    write_file_contents(f, BASE_DIR + "/management/pycom_functions/in_every_program/check_update.py")#update check

def write_optional_functions(f, sensor_object, communication_object, protocol_object):

    #Helper function for reading data
    if sensor_object.model.sensor_model == "Garmin LIDAR-Lite v3HP":
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/read_values_garmin_lidar_lite_v3HP.py")
    else:
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/read_values.py")

    #If data needs to be handled spceifically (for example shifting bits)
    if sensor_object.model.handle_data_function:
        write_file_contents(f, BASE_DIR + "/" + sensor_object.model.handle_data_function.name)
        if sensor_object.data_format.name == "JSON":
            if sensor_object.encrypt_data:
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_encrypt_JSON_handle_data.py")
            else:
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_JSON_handle_data.py")
        elif sensor_object.data_format.name == "raw":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_raw_handle_data.py")
        elif sensor_object.data_format.name == "Regatta" and protocol_object.__class__.__name__ == "HTTP":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_Regatta_handle_data_HTTP.py")
        elif sensor_object.data_format.name == "Regatta" and protocol_object.__class__.__name__ == "MQTT":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_Regatta_handle_data_MQTT.py")
    else:
        if sensor_object.data_format.name == "JSON":
            if sensor_object.encrypt_data:
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_encrypt_JSON.py")
            else:
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_JSON.py")
        elif sensor_object.data_format.name == "raw":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_raw.py")
        elif sensor_object.data_format.name == "Regatta" and protocol_object.__class__.__name__ == "HTTP":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_Regatta_HTTP.py")
        elif sensor_object.data_format.name == "Regatta" and protocol_object.__class__.__name__ == "MQTT":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/data_formatting/format_data_Regatta_MQTT.py")

    #Write connect network
    if communication_object.__class__.__name__ == "Wlan":
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/connect_network_wlan.py")

    #Write close network
    if communication_object.__class__.__name__ == "Wlan":
        write_file_contents(f, BASE_DIR + "/management/pycom_functions/close_network_wlan.py")

    #Write keep connection if NOT data_send_rate > Wlan.close_limit
    if sensor_object.data_send_rate < sensor_object.network_close_limit:
        if communication_object.__class__.__name__ == "Wlan":
            write_file_contents(f, BASE_DIR + "/management/pycom_functions/keep_connection_wlan.py")

    if protocol_object.__class__.__name__ == "HTTP" or protocol_object.__class__.__name__ == "HTTPS":
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
    elif protocol_object.__class__.__name__ == "MQTT":
        if sensor_object.network_close_limit > sensor_object.data_send_rate and sensor_object.connection_close_limit > sensor_object.data_send_rate > 0: #keep coonection
            if sensor_object.data_format.name == "JSON":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/keep_connection/MQTT_JSON.py")
            elif sensor_object.data_format.name == "raw":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/keep_connection/MQTT_raw.py")
            elif sensor_object.data_format.name == "Regatta":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/keep_connection/MQTT_Regatta.py")
        elif sensor_object.network_close_limit > sensor_object.data_send_rate > sensor_object.connection_close_limit: #close connection
            if sensor_object.data_format.name == "JSON":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_connection/MQTT_JSON.py")
            elif sensor_object.data_format.name == "raw":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_connection/MQTT_raw.py")
            elif sensor_object.data_format.name == "Regatta":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_connection/MQTT_Regatta.py")
        elif sensor_object.data_send_rate > sensor_object.network_close_limit: #close network
            if sensor_object.data_format.name == "JSON":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_network/MQTT_JSON.py")
            elif sensor_object.data_format.name == "raw":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_network/MQTT_raw.py")
            elif sensor_object.data_format.name == "Regatta":
                write_file_contents(f, BASE_DIR + "/management/pycom_functions/communicate_with_server/close_network/MQTT_Regatta.py")
    else:
        print("There's an error with protocol class.")

    if protocol_object.__class__.__name__ == "HTTP" or protocol_object.__class__.__name__ == "HTTPS":
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

def decrypt_msg(encrypted_msg, key, n=16):
    key = binascii.unhexlify(key)
    encrypted_msg = binascii.unhexlify(encrypted_msg)
    encrypted_msg_list = [encrypted_msg[i:i+n] for i in range(0, len(encrypted_msg), n)]
    cipher = AES.new(key, AES.MODE_CBC, iv=encrypted_msg_list[0])

    msg = ""
    for block in encrypted_msg_list[1:]:
    	decrypted_msg = cipher.decrypt(block)
    	msg += decrypted_msg.decode("ascii")
    	cipher = AES.new(key, AES.MODE_CBC, iv=block)
    return msg

def encrypt_msg(plain_text, key, n=16):
    key = binascii.unhexlify(key)
    padded_text = plain_text + (n - (len(plain_text) % n)) * " "
    text_as_list = [padded_text[i:i+n] for i in range(0, len(padded_text), n)]

    cipher = AES.new(key, AES.MODE_CBC)
    encrypted_string = cipher.iv

    #encryption
    for block in text_as_list:
    	ciphertext = cipher.encrypt(block.encode("ascii"))
    	encrypted_string += ciphertext
    	cipher = AES.new(key, AES.MODE_CBC, iv=ciphertext)

    encrypted_string = binascii.hexlify(encrypted_string)
    return encrypted_string

def construct_software_response_update(sensor_object, session_key):
    response = session_key + "|"
    update = Update.objects.filter(sensor=sensor_object).order_by('-date')[0]
    with open(BASE_DIR + '/management/sensor_updates/' + update.filename, 'r') as f:
        data = f.read()
    data = data.rstrip()
    response += data
    encrypted_msg = encrypt_msg(response, sensor_object.shared_secret_updates)
    h = hmac.new(binascii.unhexlify(Server.objects.all()[0].server_key), encrypted_msg, hashlib.sha256)
    hmac_msg = binascii.hexlify(h.digest())
    return encrypted_msg.decode("ascii") + "." + hmac_msg.decode("ascii")


def construct_software_response_up_to_date(sensor_object, session_key):
    response = session_key + "|"
    response += "UP-TO-DATE"
    encrypted_msg = encrypt_msg(response, sensor_object.shared_secret_updates)
    h = hmac.new(binascii.unhexlify(Server.objects.all()[0].server_key), encrypted_msg, hashlib.sha256)
    hmac_msg = binascii.hexlify(h.digest())
    return encrypted_msg.decode("ascii") + "." + hmac_msg.decode("ascii")
