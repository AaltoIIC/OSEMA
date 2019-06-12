"""Read values from sensor"""
def read_values(i2c):
    address = SETTINGS_DICT["ADDRESS"]
    read_dict = READ_DICT
    readed_values = b""
    for key in read_dict:
        readed_values += i2c.readfrom_mem(address, int(key), read_dict[key])
    return readed_values
