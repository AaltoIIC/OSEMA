def format_data(header_ts, data):
    data_string = "{\n"
    data_string += "\t'Begin':{},\n".format(header_ts)
    data_string += "\t'Data': [\n"
    for data_tuple in data:
        data_string += "\t\t {"
        data_values = ustruct.unpack(FORMAT_STRING[:-1], data_tuple[0])
        data_values = handle_data(data_values)
        i = 0
        max = len(VARIABLE_NAMES)
        for variable in VARIABLE_NAMES:
            if i == max:
                data_string += "'time':{}".format(header_ts + data_tuple[1])
            else:
                data_string += "'{}':{} , ".format(variable, data_values[i])
            i += 1
        data_string += "}\n"
    data_string += "\t]\n"
    data_string += "}\n"
    return data_string


handle_data
