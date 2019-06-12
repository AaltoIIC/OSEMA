"""Loop measurement and control often data is sent to server"""
def measure(i2c):
    print("measure continuous")
    m = Measure(i2c)

class Measure:
    def __init__(self, i2c):
        self.ip_address, self.port = SETTINGS_DICT["IP_ADDRESS_SEND"].split(":")
        self.s = create_and_connect_socket(self.ip_address, self.port)
        self.i2c = i2c
        self.rtc = RTC()
        self.rtc.init((2018, 7, 17, 10, 30, 0, 0, 0))
        sync_rtc(self.rtc)
        self.length = calculate_length()
        self.start = utime.ticks_cpu()
        self.header_ts = self.rtc.now()
        self.period_time_us = int(round((1/SETTINGS_DICT["SAMPLE_RATE_HZ"]) * 1000000))
        self.header = "BEGIN: " + str(SENSOR_ID) + ";" + SENSOR_KEY + ";" + SETTINGS_DICT["FORMAT_STRING"] + ";" + str(self.header_ts)
        self.s.send(self.header.encode("ascii"))
        self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)

    #Called every period_time_us
    def _measurement(self, alarm):
        data = read_values(self.i2c)
        timestamp = utime.ticks_diff(self.start, utime.ticks_cpu())
        self.status = send_data([[data, timestamp]], self.s, self.length)
        if self.status == CONNECTION_BROKEN:
            alarm.cancel()
            while self.status == CONNECTION_BROKEN:
                self.s.close()
                self.s = create_and_connect_socket(self.ip_address, self.port)
                #send header again
                self.s.send(self.header.encode("ascii"))
                self.status = send_data([[data, timestamp]], s, length)
            self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)
