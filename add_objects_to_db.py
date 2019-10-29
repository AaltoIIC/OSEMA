#Idea: https://www.tangowithdjango.com/book/chapters/models.html#creating-a-population-script and https://blog.robphoenix.com/python/notes-on-django-population-script/
import os

PRINT = True

def add_objects():
    """Adding necessary value pairs"""
    p0_2 = add_value_pair(0, 2)
    p2_32 = add_value_pair(2, 32)
    p2_4 = add_value_pair(2, 4)
    p2_29 = add_value_pair(2, 29)
    p2_128 = add_value_pair(2, 128)
    p2_255 = add_value_pair(2, 255)
    p4_0 = add_value_pair(4, 0)
    p4_1 = add_value_pair(4, 1)
    p4_8 = add_value_pair(4, 8)
    p15_2 = add_value_pair(15, 2)
    p18_3 = add_value_pair(18, 3)
    p18_5 = add_value_pair(18, 5)
    p28_0 = add_value_pair(28, 0)
    p28_128 = add_value_pair(28, 128)
    p28_176 = add_value_pair(28, 176)
    p32_151 = add_value_pair(32, 151)
    p32_135 = add_value_pair(32, 135)
    p32_119 = add_value_pair(32, 119)
    p32_103 = add_value_pair(32, 103)
    p32_87 = add_value_pair(32, 87)
    p32_71 = add_value_pair(32, 71)
    p32_55 = add_value_pair(32, 55)
    p32_39 = add_value_pair(32, 39)
    p32_23 = add_value_pair(32, 23)
    p36_32 = add_value_pair(36, 32)
    p36_24 = add_value_pair(36, 24)
    p36_16 = add_value_pair(36, 16)
    p36_8 = add_value_pair(36, 8)
    p36_0 = add_value_pair(36, 0)
    p40_6 = add_value_pair(40, 6)
    p44_15 = add_value_pair(44, 15)
    p44_14 = add_value_pair(44, 14)
    p44_13 = add_value_pair(44, 13)
    p44_12 = add_value_pair(44, 12)
    p44_11 = add_value_pair(44, 11)
    p44_10 = add_value_pair(44, 10)
    p44_9 = add_value_pair(44, 9)
    p44_8 = add_value_pair(44, 8)
    p44_7 = add_value_pair(44, 7)
    p44_6 = add_value_pair(44, 6)
    p44_5 = add_value_pair(44, 5)
    p44_4 = add_value_pair(44, 4)
    p44_3 = add_value_pair(44, 3)
    p44_2 = add_value_pair(44, 2)
    p44_1 = add_value_pair(44, 1)
    p44_0 = add_value_pair(44, 0)
    p45_59 = add_value_pair(45, 59)
    p49_11 = add_value_pair(49, 11)
    p49_10 = add_value_pair(49, 10)
    p49_9 = add_value_pair(49, 9)
    p49_8 = add_value_pair(49, 8)
    p50_6 = add_value_pair(50, 6)
    p56_0 = add_value_pair(56, 0)

    """Adding types of sensors"""
    seeed_grove_i2c_adc = add_type_of_sensor("seeed Grove i2C ADC", "http://wiki.seeedstudio.com/Grove-I2C_ADC/", 80, "seeed_Grove_i2C_ADC.py")
    garmin_lidar_lite_v3HP = add_type_of_sensor("Garmin LIDAR-Lite v3HP", "https://buy.garmin.com/en-US/US/p/578152/pn/010-01722-10", 98, "garmin_lidar_lite_v3HP.py")
    lis3dsh = add_type_of_sensor("LIS3DSH", "Use the following divisors to get acceleration in unit g: \n +- 2g:  divisor = 16380\n +- 4g:  divisor = 8190\n +- 8g:  divisor = 4096\n +- 16g: divisor = 1365.33\n", 29)
    adxl345 = add_type_of_sensor("ADXL345", "https://www.analog.com/media/en/technical-documentation/data-sheets/ADXL345.pdf", 83)

    """Adding senstivitys"""
    adxl345_2g = add_sensitivity(adxl345, "+-2g", write_values=[p49_8])
    adxl345_4g = add_sensitivity(adxl345, "+-4g", write_values=[p49_9])
    adxl345_8g = add_sensitivity(adxl345, "+-8g", write_values=[p49_10])
    adxl345_16g = add_sensitivity(adxl345, "+-16g", write_values=[p49_11])
    lis3dsh_2g = add_sensitivity(lis3dsh, "+-2g", write_values=[p36_0])
    lis3dsh_4g = add_sensitivity(lis3dsh, "+-4g", write_values=[p36_8])
    lis3dsh_6g = add_sensitivity(lis3dsh, "+-6g", write_values=[p36_16])
    lis3dsh_8g = add_sensitivity(lis3dsh, "+-8g", write_values=[p36_24])
    lis3dsh_16g = add_sensitivity(lis3dsh, "+-16g", write_values=[p36_32])
    seeed_grove_i2c_adc_12bit = add_sensitivity(seeed_grove_i2c_adc, "12 bit")
    garmin_lidar_lite_v3HP_default_balanced = add_sensitivity(garmin_lidar_lite_v3HP, "Default, balanced", write_values=[p2_128, p4_8, p18_5, p28_0])
    garmin_lidar_lite_v3HP_short_range_high_speed = add_sensitivity(garmin_lidar_lite_v3HP, "Short range, high speed", write_values=[p2_29, p4_8, p18_3, p28_0])
    garmin_lidar_lite_v3HP_default_range_high_speed_short_range = add_sensitivity(garmin_lidar_lite_v3HP, "Default range, higher speed at short ranges", write_values=[p2_128, p4_0, p18_3, p28_0])
    garmin_lidar_lite_v3HP_max_range = add_sensitivity(garmin_lidar_lite_v3HP, "Maximum range", write_values=[p2_255, p4_8, p18_5, p28_0])
    garmin_lidar_lite_v3HP_high_sensitivity_high_error = add_sensitivity(garmin_lidar_lite_v3HP, "High sensitivity, high error", write_values=[p2_128, p4_8, p18_5, p28_128])
    garmin_lidar_lite_v3HP_low_sensitivity_low_error = add_sensitivity(garmin_lidar_lite_v3HP, "Low sensitivity, low error", write_values=[p2_128, p4_8, p18_5, p28_0])
    garmin_lidar_lite_v3HP_short_range_high_speed_high_error = add_sensitivity(garmin_lidar_lite_v3HP, "Short range, high speed, high error", write_values=[p2_4, p4_1, p18_3, p28_0])

    """Adding sample rates"""
    adxl345_0_1 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 0.1, [p50_6], [p44_0, p45_59, p56_0], 100000, "<hhhL")
    adxl345_0_2 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 0.2, [p50_6], [p44_1, p45_59, p56_0], 100000, "<hhhL")
    adxl345_0_39 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 0.39, [p50_6], [p44_2, p45_59, p56_0], 100000, "<hhhL")
    adxl345_0_78 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 0.78, [p50_6], [p44_3, p45_59, p56_0], 100000, "<hhhL")
    adxl345_1_56 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 1.56, [p50_6], [p44_4, p45_59, p56_0], 100000, "<hhhL")
    adxl345_3_13 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 3.13, [p50_6], [p44_5, p45_59, p56_0], 100000, "<hhhL")
    adxl345_6_25 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 6.25, [p50_6], [p44_6, p45_59, p56_0], 100000, "<hhhL")
    adxl345_12_5 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 12.5, [p50_6], [p44_7, p45_59, p56_0], 100000, "<hhhL")
    adxl345_25 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 25.0, [p50_6], [p44_8, p45_59, p56_0], 100000, "<hhhL")
    adxl345_50 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 50, [p50_6], [p44_9, p45_59, p56_0], 100000, "<hhhL")
    adxl345_100 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 100, [p50_6], [p44_10, p45_59, p56_0], 100000, "<hhhL")
    adxl345_200 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 200, [p50_6], [p44_11, p45_59, p56_0], 100000, "<hhhL")
    adxl345_400 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 400, [p50_6], [p44_12, p45_59, p56_0], 100000, "<hhhL")
    adxl345_800 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 800, [p50_6], [p44_13, p45_59, p56_0], 100000, "<hhhL")
    adxl345_1600 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 1600, [p50_6], [p44_14, p45_59, p56_0], 100000, "<hhhL")
    adxl345_3200 = add_sample_rate(adxl345, [adxl345_2g, adxl345_4g, adxl345_8g, adxl345_16g], 3200, [p50_6], [p44_15, p45_59, p56_0], 100000, "<hhhL")
    lis3dsh_3_125 = add_sample_rate(lis3dsh, [lis3dsh_2g, lis3dsh_4g, lis3dsh_6g, lis3dsh_8g, lis3dsh_16g], 3.125, [p40_6], [p32_23], 100000, "<hhhL")
    lis3dsh_6_25 = add_sample_rate(lis3dsh, [lis3dsh_2g, lis3dsh_4g, lis3dsh_6g, lis3dsh_8g, lis3dsh_16g], 6.25, [p40_6], [p32_39], 100000, "<hhhL")
    lis3dsh_12_5 = add_sample_rate(lis3dsh, [lis3dsh_2g, lis3dsh_4g, lis3dsh_6g, lis3dsh_8g, lis3dsh_16g], 12.5, [p40_6], [p32_55], 100000, "<hhhL")
    lis3dsh_25 = add_sample_rate(lis3dsh, [lis3dsh_2g, lis3dsh_4g, lis3dsh_6g, lis3dsh_8g, lis3dsh_16g], 25, [p40_6], [p32_71], 100000, "<hhhL")
    lis3dsh_50 = add_sample_rate(lis3dsh, [lis3dsh_2g, lis3dsh_4g, lis3dsh_6g, lis3dsh_8g, lis3dsh_16g], 50, [p40_6], [p32_87], 100000, "<hhhL")
    lis3dsh_100 = add_sample_rate(lis3dsh, [lis3dsh_2g, lis3dsh_4g, lis3dsh_6g, lis3dsh_8g, lis3dsh_16g], 100, [p40_6], [p32_103], 100000, "<hhhL")
    lis3dsh_400 = add_sample_rate(lis3dsh, [lis3dsh_2g, lis3dsh_4g, lis3dsh_6g, lis3dsh_8g, lis3dsh_16g], 400, [p40_6], [p32_119], 100000, "<hhhL")
    lis3dsh_800 = add_sample_rate(lis3dsh, [lis3dsh_2g, lis3dsh_4g, lis3dsh_6g, lis3dsh_8g, lis3dsh_16g], 800, [p40_6], [p32_135], 100000, "<hhhL")
    lis3dsh_1600 = add_sample_rate(lis3dsh, [lis3dsh_2g, lis3dsh_4g, lis3dsh_6g, lis3dsh_8g, lis3dsh_16g], 1600, [p40_6], [p32_151], 100000, "<hhhL")
    seeed_grove_i2c_adc_1 = add_sample_rate(seeed_grove_i2c_adc, [seeed_grove_i2c_adc_12bit], 1, [p0_2], [p2_32], 100000, "<HL")
    seeed_grove_i2c_adc_2 = add_sample_rate(seeed_grove_i2c_adc, [seeed_grove_i2c_adc_12bit], 2, [p0_2], [p2_32], 100000, "<HL")
    seeed_grove_i2c_adc_4 = add_sample_rate(seeed_grove_i2c_adc, [seeed_grove_i2c_adc_12bit], 4, [p0_2], [p2_32], 100000, "<HL")
    seeed_grove_i2c_adc_10 = add_sample_rate(seeed_grove_i2c_adc, [seeed_grove_i2c_adc_12bit], 10, [p0_2], [p2_32], 100000, "<HL")
    seeed_grove_i2c_adc_25 = add_sample_rate(seeed_grove_i2c_adc, [seeed_grove_i2c_adc_12bit], 25, [p0_2], [p2_32], 100000, "<HL")
    seeed_grove_i2c_adc_50 = add_sample_rate(seeed_grove_i2c_adc, [seeed_grove_i2c_adc_12bit], 50, [p0_2], [p2_32], 100000, "<HL")
    seeed_grove_i2c_adc_100 = add_sample_rate(seeed_grove_i2c_adc, [seeed_grove_i2c_adc_12bit], 100, [p0_2], [p2_32], 100000, "<HL")
    seeed_grove_i2c_adc_200 = add_sample_rate(seeed_grove_i2c_adc, [seeed_grove_i2c_adc_12bit], 200, [p0_2], [p2_32], 100000, "<HL")
    seeed_grove_i2c_adc_400 = add_sample_rate(seeed_grove_i2c_adc, [seeed_grove_i2c_adc_12bit], 400, [p0_2], [p2_32], 100000, "<HL")
    seeed_grove_i2c_adc_800 = add_sample_rate(seeed_grove_i2c_adc, [seeed_grove_i2c_adc_12bit], 800, [p0_2], [p2_32], 100000, "<HL")
    seeed_grove_i2c_adc_1600 = add_sample_rate(seeed_grove_i2c_adc, [seeed_grove_i2c_adc_12bit], 1600, [p0_2], [p2_32], 100000, "<HL")
    garmin_lidar_lite_v3HP_0_1 = add_sample_rate(garmin_lidar_lite_v3HP, [garmin_lidar_lite_v3HP_default_balanced, garmin_lidar_lite_v3HP_short_range_high_speed, \
                                    garmin_lidar_lite_v3HP_default_range_high_speed_short_range, garmin_lidar_lite_v3HP_max_range, garmin_lidar_lite_v3HP_high_sensitivity_high_error, \
                                    garmin_lidar_lite_v3HP_low_sensitivity_low_error, garmin_lidar_lite_v3HP_short_range_high_speed_high_error], 0.1, [p15_2], [], 100000, "<HL")
    garmin_lidar_lite_v3HP_0_2 = add_sample_rate(garmin_lidar_lite_v3HP, [garmin_lidar_lite_v3HP_default_balanced, garmin_lidar_lite_v3HP_short_range_high_speed, \
                                    garmin_lidar_lite_v3HP_default_range_high_speed_short_range, garmin_lidar_lite_v3HP_max_range, garmin_lidar_lite_v3HP_high_sensitivity_high_error, \
                                    garmin_lidar_lite_v3HP_low_sensitivity_low_error, garmin_lidar_lite_v3HP_short_range_high_speed_high_error], 0.2, [p15_2], [], 100000, "<HL")
    garmin_lidar_lite_v3HP_0_5 = add_sample_rate(garmin_lidar_lite_v3HP, [garmin_lidar_lite_v3HP_default_balanced, garmin_lidar_lite_v3HP_short_range_high_speed, \
                                    garmin_lidar_lite_v3HP_default_range_high_speed_short_range, garmin_lidar_lite_v3HP_max_range, garmin_lidar_lite_v3HP_high_sensitivity_high_error, \
                                    garmin_lidar_lite_v3HP_low_sensitivity_low_error, garmin_lidar_lite_v3HP_short_range_high_speed_high_error], 0.5, [p15_2], [], 100000, "<HL")
    garmin_lidar_lite_v3HP_1 = add_sample_rate(garmin_lidar_lite_v3HP, [garmin_lidar_lite_v3HP_default_balanced, garmin_lidar_lite_v3HP_short_range_high_speed, \
                                    garmin_lidar_lite_v3HP_default_range_high_speed_short_range, garmin_lidar_lite_v3HP_max_range, garmin_lidar_lite_v3HP_high_sensitivity_high_error, \
                                    garmin_lidar_lite_v3HP_low_sensitivity_low_error, garmin_lidar_lite_v3HP_short_range_high_speed_high_error], 1.0, [p15_2], [], 100000, "<HL")
    garmin_lidar_lite_v3HP_2 = add_sample_rate(garmin_lidar_lite_v3HP, [garmin_lidar_lite_v3HP_default_balanced, garmin_lidar_lite_v3HP_short_range_high_speed, \
                                    garmin_lidar_lite_v3HP_default_range_high_speed_short_range, garmin_lidar_lite_v3HP_max_range, garmin_lidar_lite_v3HP_high_sensitivity_high_error, \
                                    garmin_lidar_lite_v3HP_low_sensitivity_low_error, garmin_lidar_lite_v3HP_short_range_high_speed_high_error], 2.0, [p15_2], [], 100000, "<HL")
    garmin_lidar_lite_v3HP_4 = add_sample_rate(garmin_lidar_lite_v3HP, [garmin_lidar_lite_v3HP_default_balanced, garmin_lidar_lite_v3HP_short_range_high_speed, \
                                    garmin_lidar_lite_v3HP_default_range_high_speed_short_range, garmin_lidar_lite_v3HP_max_range, garmin_lidar_lite_v3HP_high_sensitivity_high_error, \
                                    garmin_lidar_lite_v3HP_low_sensitivity_low_error, garmin_lidar_lite_v3HP_short_range_high_speed_high_error], 4.0, [p15_2], [], 100000, "<HL")
    garmin_lidar_lite_v3HP_10 = add_sample_rate(garmin_lidar_lite_v3HP, [garmin_lidar_lite_v3HP_default_balanced, garmin_lidar_lite_v3HP_short_range_high_speed, \
                                    garmin_lidar_lite_v3HP_default_range_high_speed_short_range, garmin_lidar_lite_v3HP_max_range, garmin_lidar_lite_v3HP_high_sensitivity_high_error, \
                                    garmin_lidar_lite_v3HP_low_sensitivity_low_error, garmin_lidar_lite_v3HP_short_range_high_speed_high_error], 10.0, [p15_2], [], 100000, "<HL")


    """Add default variables to sensors"""
    add_default_variable("acceleration_x", "mg", adxl345)
    add_default_variable("acceleration_y", "mg", adxl345)
    add_default_variable("acceleration_z", "mg", adxl345)
    add_default_variable("acceleration_x", "mg", lis3dsh)
    add_default_variable("acceleration_y", "mg", lis3dsh)
    add_default_variable("acceleration_z", "mg", lis3dsh)
    add_default_variable("analog_signal", "unit", seeed_grove_i2c_adc)
    add_default_variable("distance", "cm", garmin_lidar_lite_v3HP)

    """Adding Http"""
    http_example = add_http("HTTP", "domain.com", 80, "/path")
    """Adding MQTT"""
    mqtt_example = add_mqtt("MQTT", "some/topic", "io.adafruit.com", 1883, "username", "key")
    """Adding Wlan"""
    wlan_example = add_wlan("wlan", "ssid", Wlan.WPA2, "key")
    """Add dataformats"""
    JSON = add_dataformat("JSON")
    raw = add_dataformat("raw")
    Regatta = add_dataformat("Regatta")
    """Add superuser"""
    add_superuser("admin")
    """Add server"""
    add_server()

def add_value_pair(value1, value2):
    p = Value_pair.objects.get_or_create(value1=value1, value2=value2)[0]
    if PRINT:
        print("Value pair: {}, {} created.".format(value1, value2))
    return p

def add_type_of_sensor(sensor_model, sensor_information, address, handle_data_function="NO FUNCTION"):
    t = Type_of_sensor.objects.get_or_create(sensor_model=sensor_model, sensor_information=sensor_information, address=address)[0]
    if handle_data_function != "NO FUNCTION":
        t.handle_data_function.save(handle_data_function, File(open('handle_data_functions/{}'.format(handle_data_function), 'rb')))
    if PRINT:
        print("Type of sensor: {} created.".format(sensor_model))
    return t

def add_sensitivity(model, sensitivity, write_values=[], format_string="", read_values=[]):
    s = Sensitivity.objects.get_or_create(model=model, sensitivity=sensitivity)[0]
    if format_string != "":
        s.format_string = format_string
    for read_value in read_values:
        s.read_values.add(read_value)
    for write_value in write_values:
        s.write_values.add(write_value)
    if PRINT:
        print("Sensitivity: {} created for {}.".format(sensitivity, model.sensor_model))
    return s

def add_sample_rate(model, supported_sensitivities, sample_rate, read_values, write_values, baudrate, format_string):
    s = Sample_rate.objects.get_or_create(model=model, sample_rate=sample_rate, baudrate=baudrate, format_string=format_string)[0]
    for read_value in read_values:
        s.read_values.add(read_value)
    for write_value in write_values:
        s.write_values.add(write_value)
    for supported_sensitivity in supported_sensitivities:
        s.supported_sensitivities.add(supported_sensitivity)
    if PRINT:
        print("Samplerate: {} Hz created for {}.".format(sample_rate, model.sensor_model))
    return s

def add_http(name, data_server_url, port, path):
    h = HTTP.objects.get_or_create(name=name, path=path, data_server_url=data_server_url, data_server_port=port)
    if PRINT:
        print("HTTP: {} created.".format(name))
    return h

def add_https(name, data_server_url, port, path):
    h = HTTPS.objects.get_or_create(name=name, path=path, data_server_url=data_server_url, data_server_port=port)
    if PRINT:
        print("HTTPS: {} created.".format(name))
    return h

def add_mqtt(name, topic, broker_url, broker_port=1883, user="", key=""):
    m = MQTT.objects.get_or_create(name=name, topic=topic, broker_url=broker_url, broker_port=broker_port, user=user, key=key)
    if PRINT:
        print("MQTT: {} created.".format(name))
    return m

def add_wlan(name, ssid, security, key, username=""):
    """
    Available securities:
    Wlan.NONE
    Wlan.WEP
    Wlan.WPA
    Wlan.WPA2
    Wlan.WPA2_ENT
    """
    try:
        w = Wlan.objects.get_or_create(name=name, ssid=ssid, security=security, key=key)
        if username != "":
            w.username = username
        if PRINT:
            print("Wlan: {} created.".format(name))
        return w
    except:
        if PRINT:
            print("Wlan with similar name already exists")

def add_default_variable(name, unit, type_of_sensor):
    d = Default_variable.objects.get_or_create(name=name, unit=unit, type_of_sensor=type_of_sensor)
    if PRINT:
        print("Created default variable for {}: name: {}, unit: {}.".format(type_of_sensor.sensor_model, name, unit))
    return d

def add_dataformat(name):
    d = Data_format.objects.get_or_create(name=name)
    if PRINT:
        print("Data format {} created.".format(name))
    return d

def add_superuser(name):
    try:
        u = User.objects.create_superuser(name, 'admin@example.com', 'pas12345')
        if PRINT:
            print("Superuser", name, "created.")
    except:
        if PRINT:
            print("Superuser exists.")

def add_server():
    s = Server.objects.get_or_create()
    if PRINT:
        print("Server {} created.".format(s[0].name))


# Start execution here!
if __name__ == '__main__':
    import django
    print("Starting database population script...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sensor_management_platform.settings')
    django.setup()
    from management.models import User, Sensor, Type_of_sensor, Value_pair, Sensitivity, Sample_rate, Sensor, Wlan, Nb_iot, HTTP, HTTPS, Update, MQTT, Data_format, Variable, Default_variable, Server
    from django.core.files import File
    add_objects()
    print("Population script finished")
