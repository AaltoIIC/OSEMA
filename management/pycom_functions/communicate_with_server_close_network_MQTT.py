"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, length, header_ts, rtc):
    try:
        network = connect_network() #Connect to network
        sync_rtc(rtc)
        header = "BEGIN: " + str(SENSOR_ID) + ";" + str(header_ts) + "\n"
        data_string = header + "[\n"
        for value_pair in data_with_ts:
            data_string += "{\n"
            value_no = 1
            data_tuple = ustruct.unpack(SETTINGS_DICT["FORMAT_STRING"][:-1] ,value_pair[0])
            for value in data_tuple:
                data_string += "\t'Value" + str(value_no) + "':" + str(value) + "\n"
                value_no += 1
            data_string += "\t'Timestamp':" + str(value_pair[1]) + "\n"
            data_string += "},\n"
        data_string += "]"
        client = MQTTClient(str(SENSOR_ID), SETTINGS_DICT['DATA_SERVER_URL'],user=SETTINGS_DICT['USER'], password=SETTINGS_DICT["KEY"], port=SETTINGS_DICT["PORT"])
        client.connect()
        client.publish(topic=SETTINGS_DICT["TOPIC"], msg=data_string.encode("ascii"))
        client.disconnect()
        close_network(network)
    except OSError:
        print("OSError")
        try:
            if not network:
                network = connect_network() #Connect to network
            ip_address, port = SETTINGS_DICT["UPDATE_IP_ADDRESS"].split(":")
            s = create_and_connect_socket(ip_address, port)
            content_length = len("sensor_id={}&sensor_key={}&status=OSError".format(SENSOR_ID, SENSOR_KEY))
            data = """POST /report_failure HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\nsensor_id={}&sensor_key={}&status=OSError\r\n\r\n""".format(ip_address, content_length, SENSOR_ID, SENSOR_KEY)
            s.send(bytes(data, 'utf8'))
            utime.sleep(2)
            print("status send to user interface")
            print("resetting machine")
            machine.reset()
        except:
            print("resetting machine")
            machine.reset()
