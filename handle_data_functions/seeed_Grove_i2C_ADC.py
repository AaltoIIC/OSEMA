#test
def handle_data(data):
    reading = ((data[0] & 0x0f) << 8 | data[1]) & 0xfff
    return ustruct.pack("<H", reading)
