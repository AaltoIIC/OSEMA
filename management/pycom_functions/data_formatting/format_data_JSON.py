def format_data(header_ts, data):
    data_string = "{\n"
    data_string += "\t'Begin':{},\n".format(convert_to_epoch(header_ts))
    data_string += "\t'Data': [\n"
    for value_pair in data:
        data_string += "\t\t {"
        data_values = ustruct.unpack(FORMAT_STRING[:-1], value_pair[0])
        max = len(VARIABLE_NAMES)
        for i in range(len(VARIABLE_NAMES) + 1):
            if i == max:
                data_string += "'time':{}".format(header_ts + value_pair[1])
            else:
                data_string += "'{}':{} , ".format(variable, data_values[i])
        data_string += "}\n"
    data_string += "\t]\n"
    data_string += "}\n"
    return data_string
