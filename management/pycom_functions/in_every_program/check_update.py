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
        decoded_data = data_read.decode('ascii')
        payload_begins = decoded_data.find("import") #Payload string always begins with an import statement
        if payload_begins == -1:
            if decoded_data.find("UP-TO-DATE") != -1:
                print("Software up-to-date")
                s.close()
                return
            else:
                print("There's an error with the server response")
        else:
            data = decoded_data[payload_begins:]
            # calculate hash
            hash = uhashlib.sha256(decoded_data.encode("ascii")).digest()
            #Confirm that data is received
            content_length = len("sensor_id={}&sensor_key={}&hash={}".format(SENSOR_ID, SENSOR_KEY, hash))
            confirmation = """POST /confirm_update HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\nsensor_id={}&sensor_key={}hash={}\r\n\r\n""".format(url, content_length, SENSOR_ID, SENSOR_KEY, hash)
            p = s.send(bytes(confirmation, 'utf8'))
            data_read = b""
            while True:
                data_res = s.recv(MAXLINE)
                if data_res:
                    data_read += data_res
                else:
                    break
            decoded_data = data_read.decode('ascii')
            s.close()
            if decoded_data == "OK":
                print("update confirmed")
                f = open("new_main.txt", "w")
                f.write(data)
                f.close()
                print("Writing data succeed!")
                utime.sleep(1)
                machine.reset()
            else:
                print("Software update failed. Hash doesn't match.")
                check_update(url, port)
    except:
        print("Software update failed.")
