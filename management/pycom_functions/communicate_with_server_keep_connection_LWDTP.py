"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, length, s, header_ts):
    format_string = SETTINGS_DICT["FORMAT_STRING"]
    #send header
    header = "BEGIN: " + str(SENSOR_ID) + ";" + SENSOR_KEY  + ";" + format_string + ";" + str(header_ts)
    s.send(header.encode("ascii"))
    #wait until OK
    data = s.recv(MAXLINE)
    while data.decode('ascii') != "OK":
        data += s.recv(MAXLINE)
    #Send data
    status = send_data(data_with_ts, s, length)
    while status == CONNECTION_BROKEN:
        s.close()
        ip_address, port = SETTINGS_DICT["IP_ADDRESS_SEND"].split(":")
        s = create_and_connect_socket(ip_address, port)
        #send header again
        s.send(header.encode("ascii"))
        status = send_data(data_with_ts, s, length)
    amount_of_data_send = status
    #Send END-block
    s.send("END".encode("ascii"))
    s.send(ustruct.pack("<L", amount_of_data_send))
    s.send("KEEP".encode("ascii"))
    #Wait until OK
    data = s.recv(MAXLINE)
    string = data.decode("ascii").split(":")[0].strip()
    while string != "UPDATE" and string != "UPTODATE":
        data += s.recv(MAXLINE)
        string = data.decode("ascii").split(":")[0].strip()
    s.send("OK".encode('ascii'))
    if string == "UPDATE":
        ip_address, port = data.decode("ascii").split(":")[1:]
        write_new_main(ip_address.strip(), int(port.strip()))
