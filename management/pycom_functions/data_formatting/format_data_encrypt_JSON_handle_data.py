def format_data(header_ts, data):
    header_ts_epoch = convert_to_epoch(header_ts)
    data_string = '{\n'
    data_string += '\t"Begin":{},\n'.format(header_ts_epoch)
    data_string += '\t"Data": [\n'
    for value_pair in data:
        data_string += '\t\t {'
        value_pair[0] = handle_data(value_pair[0])
        data_values = ustruct.unpack(FORMAT_STRING[:-1], value_pair[0])
        max = len(VARIABLE_NAMES)
        for i in range(len(VARIABLE_NAMES) + 1):
            if i == max:
                data_string += '"time":{}'.format(header_ts_epoch + int(value_pair[1]/1000))
            else:
                data_string += '"{}":{}, '.format(VARIABLE_NAMES[i], data_values[i])
        data_string += '},\n'
    data_string = data_string[:-2]
    data_string += '\n'
    data_string += '\t]\n'
    data_string += '}\n'
    return encrypt_msg(data_string, SHARED_SECRET_DATA)
