def main():
    try:
        print("Entering main loop")
        i2c = I2C(0, I2C.MASTER, baudrate=SETTINGS_DICT["BAUDRATE"])
        config_sensor(i2c)

        ip_address, port = SETTINGS_DICT['UPDATE_IP_ADDRESS'].strip().split(":")
        network = connect_network()
        write_new_main(ip_address, int(port))
        close_network(network)

        _thread.start_new_thread(measure, (i2c,))
        interval = SETTINGS_DICT['UPDATE_CHECK_LIMIT']
        _thread.start_new_thread(ask_updates, (interval, ip_address, int(port)))
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
