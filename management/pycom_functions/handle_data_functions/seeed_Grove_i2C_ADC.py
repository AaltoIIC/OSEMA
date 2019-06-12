def handle_data(data):
    return ((data[0] & 0x0f) << 8 | data[1]) & 0xfff
