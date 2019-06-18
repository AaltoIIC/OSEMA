"""Asks updates at the given interval. Connects to network before asking updates"""
def ask_updates(interval, url, port):
    while True:
        network = connect_network()
        check_update(url, port)
        close_network(network)
        utime.sleep(interval)
