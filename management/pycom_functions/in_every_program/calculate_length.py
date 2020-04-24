"""Calculates how many bytes are read from sensor"""
def calculate_length():
    sum = 0
    for key in READ_DICT:
        sum += READ_DICT[key]
    return sum
