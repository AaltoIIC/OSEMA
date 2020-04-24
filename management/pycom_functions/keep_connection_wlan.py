"""Keep connection to wifi"""
def keep_connection(wlan):
    ssid, auth, identity = NETWORK_SETTINGS
    interval = 1000
    counter_max = 10
    counter = 1
    while True:
        utime.sleep_ms(interval)
        if not wlan.isconnected():
            counter += 1
            wlan.connect(ssid=ssid, auth=auth, identity=identity)
        else:
            counter = 1
        if counter == counter_max:
            counter = 1
            close_network(wlan)
            wlan = connect_network()
            