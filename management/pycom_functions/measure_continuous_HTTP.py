"""Loop measurement and control often data is sent to server"""
def measure(i2c):
    print("measure continuous")
    m = Measure(i2c)

class Measure:
    def __init__(self, i2c):
        self.i2c = i2c
        self.period_time_us = int(round((1/SAMPLE_RATE_HZ) * 1000000))
        self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)

    #Called every period_time_us
    def _measurement(self, alarm):
        data = read_values(self.i2c)
        try:
            data_string = format_data(machine.RTC().now(), [data, 0])
            content_length = len("sensor_id={}&sensor_key={}&data=".format(SENSOR_ID, SENSOR_KEY))
            content_length += len(data_string)
            string = """POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\nsensor_id={}&sensor_key={}&data={}\r\n\r\n""".format(PATH, DATA_SERVER_URL, content_length, SENSOR_ID, SENSOR_KEY, data_string)
            s = create_and_connect_socket(DATA_SERVER_URL, DATA_SERVER_PORT)
            s.send(bytes(string, 'utf8'))
            s.close()
        except:
            print("Data couldn't be sended. Resetting board.")
            machine.reset()
