"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, header_ts):
    try:
        network = connect_network() #Connect to network
        sync_rtc(machine.RTC())
        data_string = format_data(header_ts, data_with_ts)
        client = MQTTClient(str(SENSOR_ID), DATA_SERVER_URL, user=USER, password=KEY, port=PORT)
        client.connect()
        client.publish(topic=TOPIC, msg=data_string)
        client.disconnect()
        close_network(network)
    except OSError:
        print("OSError")
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
