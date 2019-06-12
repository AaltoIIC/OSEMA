"""Asks updates from the sensor configuratot at the given interval"""
def ask_updates(interval, ip_address, port):
    while True:
        write_new_main(ip_address, port)
        utime.sleep(interval)
