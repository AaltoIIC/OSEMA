"""Creates socket and connects to it. Returns socket"""
def create_and_connect_socket(url, port, use_ssl=False): #port is a string
    try:
        s = socket.socket()
    except OSError:
        print("Socket cannot be created, resetting board")
        machine.reset()
    while True:
        try:
            s.connect(socket.getaddrinfo(url, int(port))[0][-1])
            break
        except:
            pass
    if use_ssl:
        s = ssl.wrap_socket(s)
    return s
