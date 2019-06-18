from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.core.files.storage import FileSystemStorage

from django.contrib import admin
import string
import random

def data_handle_function_filename(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{}'.format("management/pycom_functions/handle_data_functions/" + instance.sensor_model + ".py")

try:
    import secrets
    def generate_password(length=20):
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(length))
except:
    def generate_password(length=20):
        return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))
# Create your models here.

#Using custom user model
class User(AbstractUser):
    USER_TYPE_CHOICES = (
    (1, 'user'),
    (2, 'manager'),
    (3, 'admin'),
    )
    email = models.EmailField(
    verbose_name='email address',
    max_length=255,
    unique=True,
    )
    auth_level = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1)

    def __str__(self):
        return '{}'.format(self.username)

class UserAdmin(admin.ModelAdmin):
    list_display  = ['username', 'first_name', 'last_name', 'email', 'id', 'password', 'is_active', 'date_joined', 'auth_level']

class Type_of_sensor(models.Model):
    sensor_model = models.CharField(max_length=50, primary_key=True)
    sensor_information = models.TextField(default="No information available")
    address = models.IntegerField(default=1)
    handle_data_function = models.FileField(upload_to=data_handle_function_filename, null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.sensor_model)

class Value_pair(models.Model):
    id = models.AutoField(primary_key=True)
    value1 = models.IntegerField()
    value2 = models.IntegerField()

    def __str__(self):
        return '{}, {}'.format(self.value1, self.value2)

class Sensitivity(models.Model):
    id = models.AutoField(primary_key=True)
    model = models.ForeignKey(Type_of_sensor, on_delete=models.CASCADE)
    sensitivity = models.CharField(max_length=50, default="Not set")
    read_values = models.ManyToManyField(Value_pair, related_name='read_values_sensitivity', blank=True)
    write_values = models.ManyToManyField(Value_pair, related_name='write_values_sensitivity', blank=True)
    format_string = models.CharField(max_length=20, blank=True) #format string send to server

    def __str__(self):
        return '{}: {}'.format(self.model, self.sensitivity)

class Sample_rate(models.Model):
    id = models.AutoField(primary_key=True)
    model = models.ForeignKey(Type_of_sensor, on_delete=models.CASCADE)
    supported_sensitivities = models.ManyToManyField(Sensitivity, related_name="supported_sensitivities")
    sample_rate = models.FloatField()
    read_values = models.ManyToManyField(Value_pair, related_name='read_values_sample_rate', blank=True)
    write_values = models.ManyToManyField(Value_pair, related_name='write_values_sample_rate', blank=True)
    baudrate = models.IntegerField(default=100000)
    format_string = models.CharField(max_length=20, default="<L") #format string send to server

    def __str__(self):
        return '{}: {}'.format(self.model, self.sample_rate)

class Sensor(models.Model):
    sensor_id = models.AutoField(primary_key=True)
    sensor_name = models.CharField(max_length=30, default="No name given")
    #on_delete=models.cacade: If sensor type is deleted all the sensors referencing to it also gets deleted
    model = models.ForeignKey(Type_of_sensor, on_delete=models.CASCADE)
    description = models.CharField(max_length=250, default="No description available")
    location = models.CharField(max_length=100, default="Location not available")
    date_added = models.DateTimeField(default=timezone.now)
    adder = models.ForeignKey(User, related_name="adder", on_delete=models.PROTECT, blank=True, null=True)
    date_modified = models.DateTimeField(default=timezone.now)
    latest_modifier = models.ForeignKey(User, related_name="latest_modifier", on_delete=models.PROTECT, blank=True, null=True)
    sensor_key = models.CharField(max_length=50, default=generate_password) #generate random 20-character alphanumeric password
    sensor_key_old = models.CharField(max_length=50, default=generate_password) #generate random 20-character alphanumeric password
    MEASURING_UP_TO_DATE = 1
    MEASURING_WAITING_FOR_UPDATE = 2
    WAITING_FOR_UPDATE = 3
    FAILURE_MEM = 4
    FAILURE_OS = 5
    FAILURE_I2C = 6
    STATUS_CHOICES = (
    (MEASURING_UP_TO_DATE, 'Measuring'),
    (MEASURING_WAITING_FOR_UPDATE, 'Measuring, Waiting-for-update'),
    (WAITING_FOR_UPDATE, 'Waiting-for-update'),
    (FAILURE_MEM, 'Failure, MemoryError'),
    (FAILURE_OS, 'Failure, OSError'),
    (FAILURE_I2C, 'Failure, I2CError'))
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    software_version = models.CharField(max_length=40, default="Intial software")
    sample_rate = models.ForeignKey(Sample_rate, on_delete=models.PROTECT, blank=True, null=True) #TODO: This has to be check to match sensor type
    sensitivity = models.ForeignKey(Sensitivity, on_delete=models.PROTECT, blank=True, null=True)
    data_send_rate = models.FloatField(default=0)
    burst_length = models.FloatField(default=0)
    burst_rate = models.FloatField(default=0)
    connection_close_limit = models.FloatField(default=3)
    network_close_limit = models.FloatField(default=30)
    update_check_limit = models.FloatField(default=3600)
    update_url = models.CharField(max_length=150, default="example.com")
    update_port = models.IntegerField(default=8000)

    #Each communication type has it's own class
    communication_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="communication_technology", blank=True, null=True)
    communication_object_id = models.PositiveIntegerField(blank=True, null=True)
    communication_object = GenericForeignKey(ct_field='communication_type', fk_field='communication_object_id')

    #Each protocol has it's own class
    protocol_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="protocol", blank=True, null=True)
    protocol_object_id = models.PositiveIntegerField(blank=True, null=True)
    protocol_object = GenericForeignKey(ct_field='protocol_type', fk_field='protocol_object_id')

    def __str__(self):
        return '{}'.format(self.sensor_name)

class Wlan(models.Model):
    NONE = "None"
    WEP = "WLAN.WEP"
    WPA = "WLAN.WPA"
    WPA2 = "WLAN.WPA2"
    WPA2_ENT = "WLAN.WPA2_ENT"
    SECURITY_CHOICES = (
        (NONE, "Nothing"),
        (WEP, "WEP"),
        (WPA, "WPA"),
        (WPA2, "WPA2"),
        (WPA2_ENT, "WPA2_ENT"),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    ssid = models.CharField(max_length=50, default="")
    security = models.CharField(max_length=13, choices=SECURITY_CHOICES, default=NONE)
    key = models.CharField(max_length=50, blank=True)
    username = models.CharField(max_length=50, blank=True)
    sensors_utilizing = GenericRelation(Sensor, object_id_field='communication_object_id', content_type_field='communication_type', related_query_name="communication_technology")

    def __str__(self):
        return 'Name: {}, ssid: {}'.format(self.name, self.ssid)

class Nb_iot(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default="default_name", unique=True)
    settings = models.CharField(max_length=50, default="default_settings")
    sensors_utilizing = GenericRelation(Sensor, object_id_field='communication_object_id', content_type_field='communication_type', related_query_name="communication_technology")

    def __str__(self):
        return 'id: {}, name: {}'.format(self.id, self.name)

class HTTP(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default="HTTP")
    data_server_url = models.CharField(max_length=150, default="Not set")
    data_server_port = models.IntegerField(default=80)
    path = models.CharField(max_length=150, default="/data")
    sensors_using = GenericRelation(Sensor, object_id_field='protocol_object_id', content_type_field='protocol_type', related_query_name="protocol")

    def __str__(self):
        return 'id: {}, name: {}'.format(self.id, self.name)

class HTTPS(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default="HTTPS")
    data_server_url = models.CharField(max_length=150, default="Not set")
    data_server_port = models.IntegerField(default=80)
    path = models.CharField(max_length=150, default="/data")
    sensors_using = GenericRelation(Sensor, object_id_field='protocol_object_id', content_type_field='protocol_type', related_query_name="protocol")

    def __str__(self):
        return 'id: {}, name: {}'.format(self.id, self.name)

#Message Queuing Telemetry Transport
class MQTT(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default="MQTT", unique=True)
    user = models.CharField(max_length=50, default="Not set")
    key = models.CharField(max_length=50, default="Not set")
    topic = models.CharField(max_length=150, default="Not set")
    broker_url = models.CharField(max_length=150, default="Not set")
    broker_port = models.IntegerField(default=1883)
    sensors_using = GenericRelation(Sensor, object_id_field='protocol_object_id', content_type_field='protocol_type', related_query_name="protocol")

    def __str__(self):
        return 'id: {}, name: {}'.format(self.id, self.name)


class Update(models.Model):
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=50, default="Invalid_filename")
    date = models.DateTimeField(default=timezone.now)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)

    def __str__(self):
        return 'sensor_id: {}, sensor_name: {}, filename: {}'.format(self.sensor.sensor_id, self.sensor.sensor_name, self.filename)

class Data_format(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return 'format_name: {}'.format(self.name)

class Variable(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    unit = models.CharField(max_length=10)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)

    def __str__(self):
        return '{}: {}'.format(self.name, self.unit)

class Default_variable(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    unit = models.CharField(max_length=10)
    type_of_sensor = models.ForeignKey(Type_of_sensor, on_delete=models.CASCADE)

    def __str__(self):
        return '{}: {} {}'.format(self.type_of_sensor.sensor_model, self.name, self.unit)
