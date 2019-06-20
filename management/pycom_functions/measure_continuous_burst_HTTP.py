"""Loop measurement and control often data is sent to server"""
def measure(i2c):
    print("Measure continuous burst")
    m = Measure(i2c)

class Measure:
    def __init__(self, i2c):
        self.i2c = i2c
        self.length = calculate_length()
        self.start = utime.ticks_cpu()
        self.header_ts = machine.RTC().now()
        self.period_time_us = int(round((1/SAMPLE_RATE_HZ) * 1000000))
        self.burst_rate = BURST_RATE
        self.current_no_of_measurements = 0
        self.no_of_measurements = int(round(BURST_LENGTH * SAMPLE_RATE_HZ)) #How many measurements is made
        self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)

    #Called every period_time_us
    def _measurement(self, alarm):
        self.header_ts = machine.RTC().now()
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
            content_length = len("sensor_id={}&sensor_key={}&Timestamp={}&data=".format(SENSOR_ID, SENSOR_KEY, self.header_ts))
            content_length += len(data_string)
            string = """POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\nsensor_id={}&sensor_key={}&Timestamp={}&data={}\r\n\r\n""".format(PATH, DATA_SERVER_URL, content_length, SENSOR_ID, SENSOR_KEY, self.header_ts, data_string)
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
