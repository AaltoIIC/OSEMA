"""Loop measurement and control often data is sent to server"""
def measure(i2c):
    print("Measure keep connection burst")
    m = Measure(i2c)

class Measure:
    def __init__(self, i2c):
        self.client = MQTTClient(str(SENSOR_ID), BROKER_URL, user=USER, password=KEY, port=BROKER_PORT)
        self.client.connect()
        self.i2c = i2c
        self.data_with_ts = []
        self.current_no_of_measurements = 0
        self.reference_point = utime.ticks_ms()
        self.sent = False
        self.no_of_measurements = int(round(BURST_LENGTH * SAMPLE_RATE_HZ)) #How many measurements is made
        self.data_send_rate = DATA_SEND_RATE_S
        self.burst_rate = BURST_RATE
        self.rtc = RTC()
        self.rtc.init((2018, 7, 17, 10, 30, 0, 0, 0))
        sync_rtc(self.rtc)
        self.start = utime.ticks_cpu()
        self.header_ts = self.rtc.now()
        self.new_header_ts = self.rtc.now()
        self.period_time_us = int(round((1/SAMPLE_RATE_HZ) * 1000000))
        self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)

    #Called every period_time_us
    def _measurement(self, alarm):
        try:
            data = read_values(self.i2c)
            timestamp = utime.ticks_diff(self.start, utime.ticks_cpu())
            self.data_with_ts.append([data, timestamp])
            self.current_no_of_measurements += 1
            if self.current_no_of_measurements == self.no_of_measurements:
                alarm.cancel()
                if utime.ticks_diff(self.reference_point, utime.ticks_ms()) > self.data_send_rate * 1000 and not self.sent:
                    self.header_ts = self.new_header_ts
                    _thread.start_new_thread(communicate_with_server, (self.data_with_ts.copy(), self.client, self.header_ts))
                    self.sent = True
                utime.sleep(self.burst_rate)
                if utime.ticks_diff(self.reference_point, utime.ticks_ms()) > self.data_send_rate * 1000 and not self.sent:
                    self.header_ts = self.new_header_ts
                    _thread.start_new_thread(communicate_with_server, (self.data_with_ts.copy(), self.client, self.header_ts))
                    self.sent = True
                if self.sent:
                    self.data_with_ts = []
                    self.start = utime.ticks_cpu()
                    self.sent = False
                    self.reference_point = utime.ticks_ms() #new reference point
                    self.new_header_ts = self.rtc.now() #new header time stamp
                self.current_no_of_measurements = 0
                self.__alarm = Timer.Alarm(self._measurement, us=self.period_time_us, periodic=True)
        except OSError as e:
            print(e)
            pycom.heartbeat(False)
            _thread.start_new_thread(send_error_msg, ("I2CError",))
            if e.args[0] == "I2C bus error":
                for i in range(10):
                    pycom.rgbled(0xFF0000)  # Red
                    utime.sleep(0.5)
                    pycom.rgbled(0x883000)  # Orange
                    utime.sleep(0.5)
            else:
                _thread.start_new_thread(send_error_msg, ("OSError",))
                for i in range(10):
                    pycom.rgbled(0xFF0000)  # Red
                    utime.sleep(0.5)
                    pycom.rgbled(0x00000)  # Black
                    utime.sleep(0.5)
            machine.reset()
        except MemoryError as e:
            gc.collect()
            print(e)
            pycom.heartbeat(False)
            _thread.start_new_thread(send_error_msg, ("MemoryError",))
            for i in range(10):
                pycom.rgbled(0xFF0000)  # Red
                utime.sleep(0.5)
                pycom.rgbled(0x0000FF)  # Blue
                utime.sleep(0.5)
            machine.reset()
