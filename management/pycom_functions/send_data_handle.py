"""Sends data to the given socket and returns amount of bytes sent. Processes data using handle_data function before sending the data"""
def send_data(data, s, length):
    bytes_sent = 0
    for value_pair in data:
        ts_packed = ustruct.pack("<L", value_pair[1])
        measurement_data = handle_data(value_pair[0])
        sent = sender(s, measurement_data + ts_packed, length)
        if sent == CONNECTION_BROKEN:
            return CONNECTION_BROKEN
        else:
            bytes_sent += sent
    return bytes_sent
