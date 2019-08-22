"""Loop measurement and control often data is sent to server"""
def measure(i2c):
    print("Measure continuous burst")
    measure_loop(i2c)

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
        data = read_values(self.i2c)
        data_string = format_data(machine.RTC().now(), [[data, 0]])
        try:
            content_length = len(data_string)
            string = """POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/octet-stream\\r\nContent-Length: {}\r\n\r\n""".format(PATH, DATA_SERVER_URL, content_length)
            s = create_and_connect_socket(DATA_SERVER_URL, DATA_SERVER_PORT)
            s = ssl.wrap_socket(s)
            s.send(bytes(string, 'utf8') + data_string)
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
