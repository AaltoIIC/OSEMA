"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, length, header_ts):
    print("communicate with server", header_ts)
    ip_address, port = SETTINGS_DICT["IP_ADDRESS_SEND"].split(":")
    format_string = SETTINGS_DICT["FORMAT_STRING"]
    s = create_and_connect_socket(ip_address, port)
    print("socket created")
    #Send header
    header = "BEGIN: " + str(SENSOR_ID) + ";" + SENSOR_KEY  + ";" + format_string + ";" + str(header_ts)
    s.send(header.encode("ascii"))
    print("Header send")
    #Wait until OK
    data = s.recv(MAXLINE)
    while data.decode('ascii') != "OK":
        data += s.recv(MAXLINE)
    print("ok received")
    #Send data
    status = send_data(data_with_ts, s, length)
    while status == CONNECTION_BROKEN:
        s.close()
        s = create_and_connect_socket(ip_address, port)
        #send header again
        s.send(header.encode("ascii"))
        status = send_data(data_with_ts, s, length)
    print("data send, amount:", status)
    amount_of_data_send = status
    #Send END-block
    s.send("END".encode("ascii"))
    s.send(ustruct.pack("<L", amount_of_data_send))
    s.send("CLSE".encode("ascii"))
    print("END, amount, CLSE sent")
    #Wait until OK
    data = s.recv(MAXLINE)
    print("the beginning of update/uptodate received")
    string = data.decode("ascii").split(":")[0].strip()
    while string != "UPDATE" and string != "UPTODATE":
        data += s.recv(MAXLINE)
        string = data.decode("ascii").split(":")[0].strip()
    print("update/uptodate received")
    s.send("OK".encode('ascii'))
    print("OK sent")
    utime.sleep(2) #Wait until OK is sent
    s.close()
    if string == "UPDATE":
        ip_address, port = data.decode("ascii").split(":")[1:]
        write_new_main(ip_address.strip(), int(port.strip()))
    print("function close", header_ts)
