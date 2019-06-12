"""Loop measurement and control often data is sent to server"""
def measure(i2c):
    print("Measure continuous burst")
    m = Measure(i2c)

class Measure:
    def __init__(self, i2c):
        self.ip_address, self.port = SETTINGS_DICT["IP_ADDRESS_SEND"].split(":")
        self.i2c = i2c
        self.rtc = RTC()
        self.rtc.init((2018, 7, 17, 10, 30, 0, 0, 0))
        sync_rtc(self.rtc)
        self.length = calculate_length()
        self.start = utime.ticks_cpu()
        self.header_ts = self.rtc.now()
        self.period_time_us = int(round((1/SETTINGS_DICT["SAMPLE_RATE_HZ"]) * 1000000))
        self.burst_rate = SETTINGS_DICT["BURST_RATE"]
        self.current_no_of_measurements = 0
        self.no_of_measurements = int(round(SETTINGS_DICT["BURST_LENGTH"] * SETTINGS_DICT["SAMPLE_RATE_HZ"])) #How many measurements is made
        self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)

    #Called every period_time_us
    def _measurement(self, alarm):
        self.header_ts = self.rtc.now()
        data = read_values(self.i2c)
        timestamp = utime.ticks_diff(self.start, utime.ticks_cpu())
        try:
            ip_address, port = SETTINGS_DICT["IP_ADDRESS_SEND"].split(":")
            s = create_and_connect_socket(ip_address, port)
            data_string = "[\n"
            data_string += "{\n"
            value_no = 1
            data_tuple = ustruct.unpack(SETTINGS_DICT["FORMAT_STRING"][:-1] , data)
            for value in data_tuple:
                data_string += "\t'Value" + str(value_no) + "':" + str(value) + "\n"
                value_no += 1
            data_string += "\t'Timestamp':" + str(timestamp) + "\n"
            data_string += "},\n"
            data_string += "]"
            content_length = len("sensor_id={}&sensor_key={}&Timestamp={}&data=".format(SENSOR_ID, SENSOR_KEY, self.header_ts))
            content_length += len(data_string)
            string = """POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\nsensor_id={}&sensor_key={}&Timestamp={}&data={}\r\n\r\n""".format(SETTINGS_DICT["PATH"], SETTINGS_DICT["IP_ADDRESS_SEND"], content_length, SENSOR_ID, SENSOR_KEY, self.header_ts, data_string)
            s.send(bytes(string, 'utf8'))
            s.close()
        except:
            print("Data couldn't be sended. Resetting board.")
            machine.reset()
        self.current_no_of_measurements += 1
        if self.current_no_of_measurements == self.no_of_measurements:
            self.current_no_of_measurements = 0
            self.start = utime.ticks_cpu()
            alarm.cancel()
            utime.sleep(self.burst_rate)
            self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)
