"""Sync clock from NTP server"""
def sync_rtc(rtc):
    rtc.ntp_sync("0.fi.pool.ntp.org", update_period=300) #sync clock from NTP server every 5 minutes
    #max no. of cycles = 10
    i = 0
    while not rtc.synced() and i < 10:
        utime.sleep(0.5)
        i += 1
