"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, length, header_ts):
    try:
        network = connect_network() #Connect to network
        sync_rtc(machine.RTC())
        header = "BEGIN: " + str(SENSOR_ID) + ";" + str(header_ts) + "\n"
        data_string = header + "[\n"
        for value_pair in data_with_ts:
            data_string += "{\n"
            value_no = 1
            data_tuple = ustruct.unpack(FORMAT_STRING[:-1], value_pair[0])
            for value in data_tuple:
                data_string += "\t'Value" + str(value_no) + "':" + str(value) + "\n"
                value_no += 1
            data_string += "\t'Timestamp':" + str(value_pair[1]) + "\n"
            data_string += "},\n"
        data_string += "]"
        client = MQTTClient(str(SENSOR_ID), DATA_SERVER_URL, user=USER, password=KEY, port=PORT)
        client.connect()
        client.publish(topic=TOPIC, msg=data_string.encode("ascii"))
        client.disconnect()
        close_network(network)
    except OSError:
        print("OSError")
        try:
            if not network:
                network = connect_network() #Connect to network
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
