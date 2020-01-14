"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, header_ts):
    try:
        network = connect_network() #Connect to network
        sync_rtc(machine.RTC())
        client = MQTTClient(str(SENSOR_ID), BROKER_URL, user=USER, password=KEY, port=BROKER_PORT)
        client.connect()
        header_ts = convert_to_epoch(header_ts)
        for value_pair in data_with_ts:
            timestamp = header_ts + int(value_pair[1] / 1000)
            data_string = format_data(timestamp, value_pair[0])
            client.publish(topic=TOPIC, msg=data_string)
        client.disconnect()
    except OSError:
        print("OSError, communicate_with_server")
        utime.sleep(5)
        try:
            if s:
                s.close()
            send_error_msg(FAILURE_OS)
            utime.sleep(2)
            print("status send to user interface")
            print("resetting machine")
            machine.reset()
        except:
            print("resetting machine")
            machine.reset()
