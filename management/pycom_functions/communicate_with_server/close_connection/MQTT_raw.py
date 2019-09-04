"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, header_ts):
    try:
        data_string = format_data(header_ts, data_with_ts)
        client = MQTTClient(str(SENSOR_ID), BROKER_URL, user=USER, password=KEY, port=BROKER_PORT)
        client.connect()
        client.publish(topic=TOPIC, msg=data_string)
        client.disconnect()
    except OSError:
        print("OSError")
        try:
            s = create_and_connect_socket(UPDATE_URL, UPDATE_PORT)
            s = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED)
            content_length = len("sensor_id={}&sensor_key={}&status=OSError".format(SENSOR_ID, SENSOR_KEY))
            data = """POST /report_failure HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\nsensor_id={}&sensor_key={}&status=OSError\r\n\r\n""".format(UPDATE_URL, content_length, SENSOR_ID, SENSOR_KEY)
            s.send(bytes(data, 'utf8'))
            utime.sleep(2)
            print("status send to user interface")
            print("resetting machine")
            s.close()
            machine.reset()
        except:
            print("resetting machine")
            machine.reset()
