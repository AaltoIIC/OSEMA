"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, header_ts):
    try:
        client = MQTTClient(str(SENSOR_ID), BROKER_URL, user=USER, password=KEY, port=BROKER_PORT)
        client.connect()
        header_ts = convert_to_epoch(header_ts)
        for value_pair in data_with_ts:
            data_values = ustruct.unpack(FORMAT_STRING[:-1], value_pair[0])
            timestamp = header_ts + value_pair[1] / 1000
            for i in range(len(VARIABLE_NAMES)):
                data_string = str(timestamp) + "," + VARIABLE_NAMES[i] + ":" + str(data_values[i])
                client.publish(topic=TOPIC, msg=data_string.encode("ascii"))
        client.disconnect()
    except OSError:
        print("OSError")
        try:
            s = create_and_connect_socket(UPDATE_URL, UPDATE_PORT)
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
