"""Sends error message to the userinterface"""
def send_error_msg(error_type):
    network = connect_network(flash_light=False) #Connect to network
    s = create_and_connect_socket(UPDATE_URL, UPDATE_PORT, UPDATE_HTTPS)
    content_length = len("sensor_id={}&sensor_key={}&status={}".format(SENSOR_ID, SENSOR_KEY, error_type))
    data = """POST /report_failure HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\nsensor_id={}&sensor_key={}&status={}\r\n\r\n""".format(UPDATE_URL, content_length, SENSOR_ID, SENSOR_KEY, error_type)
    s.send(bytes(data, 'utf8'))
    utime.sleep(2)
    print("Status sent to user interface")
