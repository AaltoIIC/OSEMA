"""Asks updates from the sensor configuratot at the given interval"""
def ask_updates(interval, url, port):
    while True:
        check_update(url, port)
        utime.sleep(interval)
