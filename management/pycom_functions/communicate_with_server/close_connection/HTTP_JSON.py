"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, header_ts):
    try:
        data_string = format_data(header_ts, data_with_ts)
        content_length = len(data_string)
        string = """POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{}""".format(PATH, DATA_SERVER_URL, content_length, data_string)
        s = create_and_connect_socket(DATA_SERVER_URL, DATA_SERVER_PORT, USE_SSL_DATA_SERVER)
        s.send(bytes(string, 'utf8'))
        s.close()
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
