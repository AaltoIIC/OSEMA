"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, client, header_ts):
    #send header
    header = "BEGIN: " + str(SENSOR_ID) + ";" + str(header_ts) + "\n"
    #constructing data string
    data_string = header + "[\n"
    for value_pair in data_with_ts:
        data_string += "{\n"
        value_no = 1
        data_tuple = ustruct.unpack(FORMAT_STRING[:-1], value_pair[0])
        for value in data_tuple:
            data_string += "\t'Value" + str(value_no) + "':" + str(value) + "\n"
            value_no += 1
        data_string += "\t'Timestamp':" + str(value_pair[1]) + "\n"
        data_string += "},\n"
    data_string += "]"
    client.publish(topic=TOPIC, msg=data_string.encode("ascii"))
