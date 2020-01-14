"""Asks update from sensor configurator with HTTP request. If a new main.py is returned writes it to the new_main.py and reboots the board"""
def check_update(url, port):
    session_key = ubinascii.hexlify(crypto.getrandbits(128)).decode("ascii")
    shared_secret = ubinascii.unhexlify(SHARED_SECRET_UPDATES)

    content = '{\n'
    content += '\t"software_version":"{}",\n'.format(SOFTWARE_VERSION)
    content += '\t"session_key":"{}"\n'.format(session_key)
    content += '}'

    encrypted_string = encrypt_msg(content, shared_secret)

    #calculate hmac_msg
    hmac_digest = hmac.HMAC(SENSOR_KEY, encrypted_string, uhashlib.sha256).digest()
    #append to msg
    encrypted_string = encrypted_string + "." + hmac_digest
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

    payload = ubinascii.unhexlify(bytes(data_read.decode("ascii").split("\r\n")[-1], "ascii"))
    msg, hmac_msg =payload.split(".")

    #compare hmac
    hmac_digest = hmac.HMAC(SERVER_KEY, encrypted_string, uhashlib.sha256).digest()
    print("hmac_digest", hmac_digest)
    print("hmac_msg", hmac_msg)
    if hmac_digest != hmac_msg:
        print("invalid hmac")
        return

    msg = decrypt_msg(msg, shared_secret)

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
