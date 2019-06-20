"""Loop measurement and control often data is sent to server"""
def measure(i2c):
    print("measure continuous")
    m = Measure(i2c)

class Measure:
    def __init__(self, i2c):
        self.client = MQTTClient(str(SENSOR_ID), BROKER_URL, user=USER, password=KEY, port=BROKER_PORT)
        self.client.connect()
        self.i2c = i2c
        self.length = calculate_length()
        self.start = utime.ticks_cpu()
        self.header_ts = machine.RTC().now()
        self.period_time_us = int(round((1/SAMPLE_RATE_HZ) * 1000000))
        self.header = "BEGIN: " + str(SENSOR_ID) + ";" + SENSOR_KEY + ";" + FORMAT_STRING + ";" + str(self.header_ts)
        self.client.publish(topic=TOPIC, msg=self.header.encode("ascii"))
        self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)

    #Called every period_time_us
    def _measurement(self, alarm):
        data = read_values(self.i2c)
        timestamp = utime.ticks_diff(self.start, utime.ticks_cpu())
        data_string = format_data(self.header_ts, [data, timestamp])
        self.client.publish(topic=TOPIC, msg=data_string.encode("ascii"))
