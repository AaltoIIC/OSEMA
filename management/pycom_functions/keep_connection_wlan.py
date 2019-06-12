"""Keep connection to wifi"""
def keep_connection(wlan):
    ssid, auth, identity = SETTINGS_DICT["NETWORK_SETTINGS"]
    interval = 3000
    while True:
        utime.sleep_ms(interval)
        if not wlan.isconnected():
            wlan.connect(ssid=ssid, auth=auth, identity=identity)
