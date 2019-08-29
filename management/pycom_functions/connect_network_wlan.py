"""Connect to wifi"""
def connect_network(flash_light=True):
    if flash_light:
        pycom.heartbeat(False)
    ssid, auth, identity = NETWORK_SETTINGS
    wlan = WLAN(mode=WLAN.STA)
    wlan.connect(ssid=ssid, auth=auth, identity=identity)
    counter = 1
    counter_max = 20 #trying to connect max 20 seconds
    while not wlan.isconnected():
        if flash_light:
            pycom.rgbled(0xCD7300) #Orange
        utime.sleep(0.5)
        if flash_light:
            pycom.rgbled(0x00000)  # Black
        utime.sleep(0.5)
        counter += 1
        if counter == counter_max:
            print("Couldn't connect to network: ", ssid, " Resetting board!")
            machine.reset()
    return wlan
