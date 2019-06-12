"""Writes the given value-address pairs to the attached sensor"""
def config_sensor(i2c):
    address = SETTINGS_DICT["ADDRESS"]
    write_dict = WRITE_DICT
    for key in write_dict:
        i2c.writeto_mem(address, int(key), write_dict[key])
