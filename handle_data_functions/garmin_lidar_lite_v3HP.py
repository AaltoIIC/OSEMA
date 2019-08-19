def handle_data(data):
    reading = data[0] << 8 | data[1]
    return ustruct.pack("<H", reading)
