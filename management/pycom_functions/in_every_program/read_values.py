"""Read values from sensor"""
def read_values(i2c):
    readed_values = b""
    for key in READ_DICT:
        readed_values += i2c.readfrom_mem(ADDRESS, int(key), read_dict[key])
    return readed_values
