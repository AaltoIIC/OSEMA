"""Covert datetime tuple to milliseconds since epoch time"""
def convert_to_epoch(datetime_tuple):
    extra_seconds = 0 #use 946684800 to get seconds from Epoch to Jan 1 2000, UTC
    ett = utime.gmtime() #used to get yearday and weekday
    seconds = utime.mktime((datetime_tuple[0], datetime_tuple[1], datetime_tuple[2], datetime_tuple[3], datetime_tuple[4], datetime_tuple[5], ett[6], ett[7]))
    return (extra_seconds + seconds) * 1000 + int(datetime_tuple[6] / 1000) #converting to milliseconds
