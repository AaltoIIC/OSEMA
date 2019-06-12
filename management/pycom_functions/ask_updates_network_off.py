"""Asks updates at the given interval. Connects to network before asking updates"""
def ask_updates(interval, ip_address, port):
    while True:
        network = connect_network()
        write_new_main(ip_address, port)
        close_network(network)
        utime.sleep(interval)
