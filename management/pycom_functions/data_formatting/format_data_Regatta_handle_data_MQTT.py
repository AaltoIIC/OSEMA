"""Format data to be sent over MQTT. Handle data"""
def format_data(timestamp, data): #timestamp is already converted to epoch
    data = handle_data(data)
    data_values = ustruct.unpack(FORMAT_STRING[:-1], data)
    data_string = str(timestamp)
    for i in range(len(VARIABLE_NAMES)):
        data_string += "," + VARIABLE_NAMES[i] + ":" + str(data_values[i])
    return data_string
