"""formatting data for Regatta Platform"""
def format_data(header_ts, data):
    data_string_list = []
    for variable in VARIABLE_NAMES:
        data_string = '{\n'
        data_string += '"\tnames": ["{}"]\n'.format(variable)
        data_string += '"\tvalueRows": [\n'
        data_string_list.append(data_string)
    j = 0
    max_j = len(data) - 1
    for value_pair in data:
        value_pair[0] = handle_data(value_pair[0])
        data_values = ustruct.unpack(FORMAT_STRING[:-1], value_pair[0])
        for i in range(len(VARIABLE_NAMES)):
            if j != max_j:
                data_string_list[i] += '\t\t{ "timestamp": {}, "values": [ {} ] },\n'.format(VARIABLE_NAMES[i], data_values[i])
            else:
                data_string_list[i] += '\t\t{ "timestamp": {}, "values": [ {} ] }\n'.format(VARIABLE_NAMES[i], data_values[i])
        j += 1
    for data_string in data_string_list:
        data_string += "\t]\n"
        data_string += "}\n"
    return data_string_list
