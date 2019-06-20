"""This function keeps rtc clock synced"""
def keep_rtc_synced(rtc):
    while True:
        sync_rtc(rtc)
        utime.sleep(3600) #clock is synced once in an hour
