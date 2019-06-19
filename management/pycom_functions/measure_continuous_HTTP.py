"""Loop measurement and control often data is sent to server"""
def measure(i2c):
    print("measure continuous")
    m = Measure(i2c)

class Measure:
    def __init__(self, i2c):
        self.i2c = i2c
        self.rtc = RTC()
        self.rtc.init((2018, 7, 17, 10, 30, 0, 0, 0))
        sync_rtc(self.rtc)
        self.length = calculate_length()
        self.start = utime.ticks_cpu()
        self.header_ts = self.rtc.now()
        self.period_time_us = int(round((1/SAMPLE_RATE_HZ) * 1000000))
        self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)

    #Called every period_time_us
    def _measurement(self, alarm):
        self.header_ts = self.rtc.now()
        data = read_values(self.i2c)
        timestamp = utime.ticks_diff(self.start, utime.ticks_cpu())
        try:
            s = create_and_connect_socket(DATA_SERVER_URL, DATA_SERVER_PORT)
            data_string = "[\n"
            data_string += "{\n"
            value_no = 1
            data_tuple = ustruct.unpack(FORMAT_STRING[:-1] , data)
            for value in data_tuple:
                data_string += "\t'Value" + str(value_no) + "':" + str(value) + "\n"
                value_no += 1
            data_string += "\t'Timestamp':" + str(timestamp) + "\n"
            data_string += "},\n"
            data_string += "]"
            content_length = len("sensor_id={}&sensor_key={}&data=".format(SENSOR_ID, SENSOR_KEY))
            content_length += len(data_string)
            string = """POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\nsensor_id={}&sensor_key={}&data={}\r\n\r\n""".format(PATH, DATA_SERVER_URL, content_length, SENSOR_ID, SENSOR_KEY, data_string)
            s.send(bytes(string, 'utf8'))
            s.close()
        except:
            print("Data couldn't be sended. Resetting board.")
            machine.reset()
