def format_data(header_ts, data):
    data_string = "Begin:{}\n".format(convert_to_epoch(header_ts))
    data_string += "Variables:{"
    for variable in VARIABLE_NAMES:
        data_string += str(variable) + ", "
    data_string += "time }\n"
    data_string += "Data:"
    for value_pair in data:
        ts_packed = ustruct.pack("<L", value_pair[1])
        data_string += handle_data(value_pair[0]) + ts_packed
    return data_string
