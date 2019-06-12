"""Reads the given amount of data form the socket"""
def read_data(s, length):
    data = s.recv(length)
    while len(data) < length:
        data += s.recv(len(data) - length)
    return data
