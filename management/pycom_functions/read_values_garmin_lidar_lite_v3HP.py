"""Read values from sensor"""
def read_values(i2c):
    i2c.writeto_mem(ADDRESS, 0, 2) #Start measurement
    busy = b"1"
    while (busy[0] & 1) != 0:
        busy = i2c.readfrom_mem(ADDRESS, 1, 1) #wait until measurement is done
    readed_values = b""
    for key in READ_DICT:
        readed_values += i2c.readfrom_mem(ADDRESS, int(key), READ_DICT[key])
    return readed_values
