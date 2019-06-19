def format_data(header_ts, data):
    data_string = "{\n"
    data_string += "\t'Begin':{},\n".format(header_ts)
    data_string += "\t'Data': [\n"
    for data_tuple in data:
        data_string += "\t\t {"
        data_tuple = ustruct.unpack(FORMAT_STRING, data_tuple)
        i = 0
        max = len(VARIABLE_NAMES)
        for variable in VARIABLE_NAMES:
            if i == max:
                data_string += "'time':{}".format(header_ts + data_tuple[i])
            else:
                data_string += "'{}':{} , ".format(variable, data_tuple[i])
            i += 1
        data_string += "}\n"
    data_string += "\t]\n"
    data_string += "}\n"
    return data_string
