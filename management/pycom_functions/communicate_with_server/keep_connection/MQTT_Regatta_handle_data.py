"""This function takes care that correct messages are sent to server"""
def communicate_with_server(data_with_ts, client, header_ts):
    header_ts = convert_to_epoch(header_ts)
    for value_pair in data_with_ts:
        value_pair[0] = handle_data(value_pair[0])
        data_values = ustruct.unpack(FORMAT_STRING[:-1], value_pair[0])
        timestamp = header_ts + value_pair[1] / 1000
        for i in range(len(VARIABLE_NAMES)):
            data_string = str(timestamp) + "," + VARIABLE_NAMES[i] + ":" + data_values[i]
            client.publish(topic=TOPIC, msg=data_string.encode("ascii"))
