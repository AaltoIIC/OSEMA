"""Asks update from sensor configurator with HTTP request. If a new main.py is returned writes it to the new_main.py and reboots the board"""
def check_update(url, port):
    try:
        addr = socket.getaddrinfo(url, int(port))[0][-1]
        s = socket.socket()
        s.connect(addr)
        s = ssl.wrap_socket(s)
        session_key = crypto.getrandbits(128)

        content = '{\n'
        content += '\t"sensor_id":"{}",\n'.format(SENSOR_ID)
        content += '\t"sensor_key":"{}",\n'.format(SENSOR_KEY)
        content += '\t"software_version":"{}",\n'.format(SOFTWARE_VERSION)
        content += '\t"session_key":"{}"\n'.format(session_key)
        content += '}'

        #Encrypt content
        n = 16
        padded_content = content + (len(content) % n) * " " #pad content
        padded_content_list = [padded_content[i:i+n] for i in range(0, len(padded_content), n)] #divide into list

        iv = crypto.getrandbits(128) # hardware generated random IV (never reuse it)
        cipher = AES(SHARED_SECRET, AES.MODE_CBC, iv)
        encrypted_string = iv

        #encryption
        for block in padded_content_list:
        	ciphertext = cipher.encrypt(block.encode())
        	encrypted_string += ciphertext
        	cipher = AES(SHARED_SECRET, AES.MODE_CBC, ciphertext)

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

        #decrypt read data
        n = 16
        encrypted_data_list = [data_read[i:i+n] for i in range(0, len(data_read), n)]
        cipher = AES(SHARED_SECRET, AES.MODE_CBC, iv=encrypted_data_list[0])
        msg = ""
        for block in encrypted_data_list[1:]:
        	decrypted_msg = cipher.decrypt(block)
        	msg += decrypted_msg.decode()
        	cipher = AES(SHARED_SECRET, AES.MODE_CBC, iv=block)

        #handle data
        payload_list = msg.split("|")
        if not (payload_list[0] == SENSOR_KEY and payload_list[1] == session_key):
            return #invalid response from the server
        hash_r = payload_list[2]
        if hash_r == "UP-TO-DATE":
            print("Software up to date.")
            return
        else:
            hash = ubinascii.hexlify(uhashlib.sha256(payload_list[3].digest()).decode("ascii")
            if hash == hash_r:
                f = open("new_main.txt", "w")
                f.write(payload_list[3])
                f.close()
                print("Writing data succeed!")
                utime.sleep(1)
                machine.reset()
            else:
                print("software update failed. Hashes doesn't match")
    except:
        print("Software update failed.")
