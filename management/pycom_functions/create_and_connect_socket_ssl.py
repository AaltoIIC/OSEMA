"""Creates socket and connects to it. Returns socket"""
def create_and_connect_socket(ip_address, port): #port is a string
    try:
        s = socket.socket()
    except OSError:
        print("Socket cannot be created, resetting board")
        machine.reset()
    s = ssl.wrap_socket(s)
    while True:
        try:
            s.connect(socket.getaddrinfo(ip_address, int(port))[0][-1])
            break
        except:
            pass
    return s
