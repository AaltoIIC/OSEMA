"""Asks update from sensor configurator with HTTP request. If a new main.py is returned writes it to the new_main.py and reboots the board"""
def check_update(url, port):
    session_key = ubinascii.hexlify(crypto.getrandbits(128)).decode("ascii")
    shared_secret_binary = ubinascii.unhexlify(SHARED_SECRET_UPDATES)
    sensor_key_binary = ubinascii.unhexlify(SENSOR_KEY)
    server_key_binary = ubinascii.unhexlify(SERVER_KEY)

    content = '{\n'
    content += '\t"software_version":"{}",\n'.format(SOFTWARE_VERSION)
    content += '\t"session_key":"{}"\n'.format(session_key)
    content += '}'

    encrypted_string = encrypt_msg(content, shared_secret_binary)

    #calculate hmac
    hmac_digest = HMAC(sensor_key_binary, encrypted_string, uhashlib.sha256).digest()
    hmac_digest_str = ubinascii.hexlify(hmac_digest).decode('ascii')
    #append to msg
    encrypted_string = encrypted_string + "." + hmac_digest_str
    #send data
    content_length = len(encrypted_string)
    msg = """POST /get_update/{} HTTP/1.1\r\nHost: {}\r\nContent-Type: text/plain\r\nContent-Length: {}\r\n\r\n{}\r\n\r\n""".format(SENSOR_ID, url, content_length, encrypted_string)
    s = create_and_connect_socket(url, port, UPDATE_HTTPS)
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

    payload = data_read.decode("ascii").split("\r\n")[-1]
    msg, hmac_msg = payload.split(".")

    #compare hmac
    hmac_digest = HMAC(server_key_binary, msg, uhashlib.sha256).digest()
    if ubinascii.hexlify(hmac_digest).decode('ascii') != hmac_msg:
        print("invalid hmac")
        return

    msg = decrypt_msg(ubinascii.unhexlify(msg), shared_secret_binary)

    #handle data
    payload_list = msg.split("|")
    if payload_list[0] != session_key:
        print("invalid response from update server")
        return #invalid response from the server
    software = payload_list[1]
    if software.rstrip() == "UP-TO-DATE":
        print("Software up to date.")
        return
    else:
        software = "|".join(payload_list[1:]).rstrip()
        f = open("new_main.txt", "w")
        f.write(software)
        f.close()
        print("Writing data succeed!")
        utime.sleep(1)
        machine.reset()
