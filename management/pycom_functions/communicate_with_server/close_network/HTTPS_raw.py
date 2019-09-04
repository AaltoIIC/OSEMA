"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, header_ts):
    try:
        network = connect_network() #Connect to network
        sync_rtc(machine.RTC())
        data_string = format_data(header_ts, data_with_ts)
        content_length = len(data_string)
        string = """POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/octet-stream\r\nContent-Length: {}\r\n\r\n""".format(PATH, DATA_SERVER_URL, content_length)
        s = create_and_connect_socket(DATA_SERVER_URL, DATA_SERVER_PORT)
        s = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED)
        s.send(bytes(string, 'utf8') + data_string)
        utime.sleep(2)
        s.close()
        close_network(network)
    except OSError:
        print("OSError")
        try:
            if not network:
                network = connect_network() #Connect to network
            if not s:
                s = create_and_connect_socket(UPDATE_URL, UPDATE_PORT)
            else:
                s.close()
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
