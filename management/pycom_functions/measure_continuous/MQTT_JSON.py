"""Loop measurement and control often data is sent to server"""
def measure(i2c):
    print("measure continuous")
    measure_loop(i2c)

class Measure:
    def __init__(self, i2c):
        self.client = MQTTClient(str(SENSOR_ID), BROKER_URL, user=USER, password=KEY, port=BROKER_PORT)
        self.client.connect()
        self.i2c = i2c
        self.period_time_us = int(round((1/SAMPLE_RATE_HZ) * 1000000))
        self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)

    #Called every period_time_us
    def _measurement(self, alarm):
        data = read_values(self.i2c)
        data_string = format_data(machine.RTC().now(), [[data, 0]])
        try:
            self.client.publish(topic=TOPIC, msg=data_string)
        except:
            print("Data couldn't be published, resetting board!")
            machine.reset()
