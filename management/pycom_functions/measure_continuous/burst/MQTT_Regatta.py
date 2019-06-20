"""Loop measurement and control often data is sent to server"""
def measure(i2c):
    print("Measure continuous burst")
    m = Measure(i2c)

class Measure:
    def __init__(self, i2c):
        self.client = MQTTClient(str(SENSOR_ID), BROKER_URL, user=USER, password=KEY, port=BROKER_PORT)
        self.client.connect()
        self.i2c = i2c
        self.period_time_us = int(round((1/SAMPLE_RATE_HZ) * 1000000))
        self.burst_rate = BURST_RATE
        self.current_no_of_measurements = 0
        self.no_of_measurements = int(round(BURST_LENGTH * SAMPLE_RATE_HZ)) #How many measurements is made
        self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)

    #Called every period_time_us
    def _measurement(self, alarm):
        data = read_values(self.i2c)
        data_values = ustruct.unpack(FORMAT_STRING[:-1], data)
        timestamp = convert_to_epoch(machine.RTC().now())
        for i in range(len(VARIABLE_NAMES)):
            data_string = str(timestamp) + "," + VARIABLE_NAMES[i] + ":" + data_values[i]
            self.client.publish(topic=TOPIC, msg=data_string.encode("ascii"))
        self.current_no_of_measurements += 1
        if self.current_no_of_measurements == self.no_of_measurements:
            self.current_no_of_measurements = 0
            alarm.cancel()
            utime.sleep(self.burst_rate)
            self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)
