"""Covert datetime tuple to milliseconds since epoch time"""
def convert_to_epoch(datetime_tuple):
    extra_seconds = 946684800 #seconds from Epoch to Jan 1 2000, UTC
    ett = utime.gmtime() #used to get yearday and weekday
    seconds = utime.mktime((ett[0], ett[1], ett[2], ett[3], ett[4], datetime_tuple[5], ett[6], ett[7]))
    return (extra_seconds + seconds) * 1000 + datetime_tuple[6] / 1000 #converting to milliseconds
