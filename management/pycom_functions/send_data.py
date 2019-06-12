"""Sends data to the given socket and returns total amount of bytes sent"""
def send_data(data, s, length):
    bytes_sent = 0
    for value_pair in data:
        ts_packed = ustruct.pack("<L", value_pair[1])
        sent = sender(s, value_pair[0] + ts_packed, length)
        if sent == CONNECTION_BROKEN:
            return CONNECTION_BROKEN
        else:
            bytes_sent += sent
    return bytes_sent
