"""Calculates how many bytes are read from sensor"""
def calculate_length():
    read_dict = READ_DICT
    sum = 0
    for key in read_dict:
        sum += read_dict[key]
    return sum
