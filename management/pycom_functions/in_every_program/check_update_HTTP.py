"""Asks update from sensor configurator with HTTP request. If a new main.py is returned writes it to the new_main.py and reboots the board"""
def check_update(url, port):
    addr = socket.getaddrinfo(url, int(port))[0][-1]
    s = socket.socket()
    s.connect(addr)
    session_key = ubinascii.hexlify(crypto.getrandbits(128)).decode("ascii")
    shared_secret = ubinascii.unhexlify(SHARED_SECRET_UPDATES)

    content = '{\n'
    content += '\t"sensor_id":"{}",\n'.format(SENSOR_ID)
    content += '\t"sensor_key":"{}",\n'.format(SENSOR_KEY)
    content += '\t"software_version":"{}",\n'.format(SOFTWARE_VERSION)
    content += '\t"session_key":"{}"\n'.format(session_key)
    content += '}'

    encrypted_string = encrypt_msg(content, shared_secret)
    #send data
    content_length = len(encrypted_string)
    msg = """POST /get_update/{} HTTP/1.1\r\nHost: {}\r\nContent-Type: text/plain\r\nContent-Length: {}\r\n\r\n{}\r\n\r\n""".format(SENSOR_ID, url, content_length, encrypted_string)
    s.send(bytes(msg, 'utf8'))

    #read response
    data_read = b""
    data_length = 0
    while True:
        data = s.recv(MAXLINE)
        data_length += len(data)
        if data:
            data_read += data
        elif data_length > MAX_SOFTWARE_SIZE:
            return #prevent buffer overflow
        else:
            break
    s.close()

    payload = ubinascii.unhexlify(bytes(data_read.decode("ascii").split("\r\n")[-1], "ascii"))
    msg = decrypt_msg(payload, shared_secret)

    #handle data
    payload_list = msg.split("|")
    if not (payload_list[0] == SERVER_ID and payload_list[1] == session_key):
        print("invalid response from update server")
        return #invalid response from the server
    hash_r = payload_list[2]
    if hash_r.rstrip() == "UP-TO-DATE":
        print("Software up to date.")
        return
    else:
        software = "|".join(payload_list[3:]).rstrip()
        hash = ubinascii.hexlify(uhashlib.sha256(software).digest()).decode("ascii")
        if hash == hash_r:
            f = open("new_main.txt", "w")
            f.write(software)
            f.close()
            print("Writing data succeed!")
            utime.sleep(1)
            machine.reset()
        else:
            print("software update failed. Hashes doesn't match")
