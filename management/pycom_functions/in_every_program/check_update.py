"""Asks update from sensor configurator with HTTP request. If a new main.py is returned writes it to the new_main.py and reboots the board"""
def check_update(url, port):
    try:
        addr = socket.getaddrinfo(url, int(port))[0][-1]
        s = socket.socket()
        s.connect(addr)
        s = ssl.wrap_socket(s)
        content_length = len("sensor_id={}&sensor_key={}&software_version={}".format(SENSOR_ID, SENSOR_KEY, SOFTWARE_VERSION))
        string = """POST /get_update HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\nsensor_id={}&sensor_key={}&software_version={}\r\n\r\n""".format(url, content_length, SENSOR_ID, SENSOR_KEY, SOFTWARE_VERSION)
        s.send(bytes(string, 'utf8'))
        data_read = b""
        while True:
            data = s.recv(MAXLINE)
            if data:
                data_read += data
            else:
                break
        s.close()
        decoded_data = data_read.decode('ascii')
        payload_begins = decoded_data.find("import") #Payload string always begins with an import statement
        if payload_begins == -1:
            if decoded_data.find("UP-TO-DATE") != -1:
                print("Software up-to-date")
                return
            else:
                print("There's an error with the server response")
        else:
            data = decoded_data[payload_begins:]
            f = open("new_main.txt", "w")
            f.write(data)
            f.close()
            print("Writing data succeed!")
            #Confirm that data is received
            s = socket.socket()
            s.connect(addr)
            content_length = len("sensor_id={}&sensor_key={}".format(SENSOR_ID, SENSOR_KEY))
            confirmation = """POST /confirm_update HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\nsensor_id={}&sensor_key={}\r\n\r\n""".format(url, content_length, SENSOR_ID, SENSOR_KEY)
            p = s.send(bytes(confirmation, 'utf8'))
            s.close()
            print("update confirmed")
            utime.sleep(1)
            machine.reset()
    except:
        print("Software update failed.")
