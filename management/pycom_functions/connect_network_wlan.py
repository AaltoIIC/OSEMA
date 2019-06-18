"""Connect to wifi"""
def connect_network(flash_light=True):
    if flash_light:
        pycom.heartbeat(False)
    ssid, auth, identity = NETWORK_SETTINGS
    wlan = WLAN(mode=WLAN.STA)
    wlan.connect(ssid=ssid, auth=auth, identity=identity)
    while not wlan.isconnected():
        if flash_light:
            pycom.rgbled(0xCD7300) #Orange
        utime.sleep(0.5)
        if flash_light:
            pycom.rgbled(0x00000)  # Black
        utime.sleep(0.5)
    return wlan
