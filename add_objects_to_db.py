#Idea: https://www.tangowithdjango.com/book/chapters/models.html#creating-a-population-script and https://blog.robphoenix.com/python/notes-on-django-population-script/

PRINT = True

import os

def add_objects():
    """Adding necessary value pairs"""
    add_value_pair(0, 2)
    add_value_pair(2, 32)
    add_value_pair(32, 151)
    add_value_pair(32, 135)
    add_value_pair(32, 119)
    add_value_pair(32, 103)
    add_value_pair(32, 87)
    add_value_pair(32, 71)
    add_value_pair(32, 55)
    add_value_pair(32, 39)
    add_value_pair(32, 23)
    add_value_pair(36, 32)
    add_value_pair(36, 24)
    add_value_pair(36, 16)
    add_value_pair(36, 8)
    add_value_pair(36, 0)
    add_value_pair(40, 6)
    add_value_pair(44, 15)
    add_value_pair(44, 14)
    add_value_pair(44, 13)
    add_value_pair(44, 12)
    add_value_pair(44, 11)
    add_value_pair(44, 10)
    add_value_pair(44, 9)
    add_value_pair(44, 8)
    add_value_pair(44, 7)
    add_value_pair(44, 6)
    add_value_pair(44, 5)
    add_value_pair(44, 4)
    add_value_pair(44, 3)
    add_value_pair(44, 2)
    add_value_pair(44, 1)
    add_value_pair(44, 0)
    add_value_pair(45, 59)
    add_value_pair(49, 11)
    add_value_pair(49, 10)
    add_value_pair(49, 9)
    add_value_pair(49, 8)
    add_value_pair(50, 6)
    """Adding types of sensors"""
    add_type_of_sensor("seeed Grove i2C ADC", "http://wiki.seeedstudio.com/Grove-I2C_ADC/", 80, "seeed_Grove_i2C_ADC.py")
    add_type_of_sensor("LIS3DSH", "Use the following divisors to get acceleration in unit g: \n +- 2g:  divisor = 16380\n +- 4g:  divisor = 8190\n +- 8g:  divisor = 4096\n +- 16g: divisor = 1365.33\n", 29)
    add_type_of_sensor("ADXL345", "https://www.analog.com/media/en/technical-documentation/data-sheets/ADXL345.pdf", 83)
    """Adding senstivitys"""
    """Adding sample rates"""
    """Adding Http"""
    """Adding MQTT"""


def add_value_pair(value1, value2):
    p = Value_pair.objects.get_or_create(value1=value1, value2=value2)[0]
    if PRINT:
        print("Value pair: {}, {} created.".format(value1, value2))
    return p

def add_type_of_sensor(sensor_model, sensor_information, address, handle_data_function="NO FUNCTION"):
    t = Type_of_sensor.objects.get_or_create(sensor_model=sensor_model, sensor_information=sensor_information, address=address, handle_data_function=handle_data_function)[0]
    if handle_data_function != "NO FUNCTION":
        print("meni tanne")
        t.handle_data_function.save(handle_data_function, File(open('handle_data_functions/{}'.format(handle_data_function), 'rb')))
    if PRINT:
        print("Type of sensor: {} created.".format(sensor_model))
    return t

# Start execution here!
if __name__ == '__main__':
    import django
    print("Starting database population script...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sensor_management_platform.settings')
    django.setup()
    from management.models import User, Sensor, Type_of_sensor, Value_pair, Sensitivity, Sample_rate, Sensor, Wlan, Nb_iot, Http, Https, Update, LWDTP, MQTT
    from django.core.files import File
    add_objects()
    print("Population script finished")
