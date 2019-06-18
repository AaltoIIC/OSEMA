"""Writes the given value-address pairs to the attached sensor"""
def config_sensor(i2c):
    for key in WRITE_DICT:
        i2c.writeto_mem(ADDRESS, int(key), write_dict[key])
