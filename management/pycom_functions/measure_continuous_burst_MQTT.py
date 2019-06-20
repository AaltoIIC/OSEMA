"""Loop measurement and control often data is sent to server"""
def measure(i2c):
    print("Measure continuous burst")
    m = Measure(i2c)

class Measure:
    def __init__(self, i2c):
        self.client = MQTTClient(str(SENSOR_ID), BROKER_URL, user=USER, password=KEY, port=BROKER_PORT)
        self.client.connect()
        self.i2c = i2c
        self.length = calculate_length()
        self.start = utime.ticks_cpu()
        self.header_ts = utime.time()
        self.period_time_us = int(round((1/SAMPLE_RATE_HZ) * 1000000))
        self.burst_rate = BURST_RATE
        self.current_no_of_measurements = 0
        self.no_of_measurements = int(round(BURST_LENGTH * SAMPLE_RATE_HZ)) #How many measurements is made
        self.header = "BEGIN: " + str(SENSOR_ID) + ";" + SENSOR_KEY + ";" + FORMAT_STRING + ";" + str(self.header_ts)
        self.client.publish(topic=TOPIC, msg=self.header.encode("ascii"))
        self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)

    #Called every period_time_us
    def _measurement(self, alarm):
        data = read_values(self.i2c)
        timestamp = utime.ticks_diff(self.start, utime.ticks_cpu())
        data_string = "{\n"
        value_no = 1
        data_tuple = ustruct.unpack(FORMAT_STRING[:-1] , data)
        for value in data_tuple:
            data_string += "\t'Value" + str(value_no) + "':" + str(value) + "\n"
            value_no += 1
        data_string += "\t'Timestamp':" + str(timestamp) + "\n"
        data_string += "}"
        self.client.publish(topic=TOPIC, msg=data_string.encode("ascii"))
        self.current_no_of_measurements += 1
        if self.current_no_of_measurements == self.no_of_measurements:
            self.current_no_of_measurements = 0
            alarm.cancel()
            utime.sleep(self.burst_rate)
            self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)
