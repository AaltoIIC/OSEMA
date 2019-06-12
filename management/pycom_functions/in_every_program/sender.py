"""Helper function to send data. Checks that every byte is sent.""" #From: https://docs.python.org/3/howto/sockets.html#socket-howto
def sender(s, data, length):
    try:
        totalsent = 0
        while totalsent < length:
            sent = s.send(data[totalsent:])
            if sent == 0:
                print("socket connection broken")
                return CONNECTION_BROKEN
            totalsent = totalsent + sent
        return totalsent
    except:
        print("Data sending failed")
        return CONNECTION_BROKEN
