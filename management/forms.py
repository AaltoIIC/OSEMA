from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from management.models import User, Sensor, Type_of_sensor, Sample_rate, Wlan, Nb_iot, HTTP, HTTPS, MQTT
from django.forms.widgets import PasswordInput, TextInput, Select, Textarea, ClearableFileInput
from django.contrib import admin

class ModifySensorForm(forms.ModelForm):
    sensor_name = forms.CharField(max_length=30, widget=TextInput(attrs={'class':'form-control'}))
    sensor_id = forms.IntegerField(required=False, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    description = forms.CharField(help_text="You can give a short description for the sensor. This field is not required.", required=False, max_length=250, widget=TextInput(attrs={'class':'form-control'}))
    location = forms.CharField(help_text="The location of the sensor. This field is not required.", required=False, max_length=100, widget=TextInput(attrs={'class':'form-control'}))
    sensor_key = forms.CharField(help_text="This is the password of the sensor, which is used with sensor key to authenticate sensor. Can contain 50 characters.", max_length=50, widget=TextInput(attrs={'class':'form-control'}))
    data_send_rate = forms.IntegerField(help_text="How often data is sent to the data server in seconds. For example value 100 means that data is sent every 100 seconds. This determines how many measurements are in one file, since each sending consist of single data file.", widget=TextInput(attrs={'class':'form-control'}))
    burst_length = forms.FloatField(help_text="The length of burst in seconds. Use '.' as a decimal separator. 0 = continuous measurement", widget=TextInput(attrs={'class':'form-control'}))
    burst_rate = forms.FloatField(help_text="Time between bursts in seconds. Time is measured form the end of the burst until the beginning of the next burst. For example, if burst length = 5 and burst rate = 10, the measurement takes 5 seconds and then program waits 10 second before it starts measuring again. Use '.' as a decimal separator.", widget=TextInput(attrs={'class':'form-control'}))
    connection_close_limit = forms.FloatField(help_text="Time in seconds after connection is closed. If data send rate is larger than this, connection is closed between sendings. Use '.' as a decimal separator.", widget=TextInput(attrs={'class':'form-control'}))
    network_close_limit = forms.FloatField(help_text="Time in seconds after the network is closed. If data send rate larger than this value, network is closed between sendings. Use '.' as a decimal separator.", widget=TextInput(attrs={'class':'form-control'}))
    update_check_limit = forms.FloatField(help_text="How often update check is done in seconds.", widget=TextInput(attrs={'class':'form-control'}))
    update_url = forms.CharField(help_text="The URL or IP-address of the server, where updates are fetched. Usually the same address as the address of this page. Insert the address in form: 255.255.255.255 or example.com", max_length=150, widget=TextInput(attrs={'class':'form-control'}))
    update_port = forms.IntegerField(widget=TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = Sensor
        fields = ['sensor_name', 'sensor_id', 'model', 'description', 'location', 'sensor_key', 'data_send_rate', 'burst_length', 'burst_rate', 'connection_close_limit', 'network_close_limit', 'update_check_limit', 'update_url', 'update_port']

class ModifySensorFormLocked(forms.ModelForm):
    sensor_name = forms.CharField(max_length=30, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    sensor_id = forms.CharField(max_length=30, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    sensor_key = forms.CharField(help_text="This is the password of the sensor, which is used with sensor key to authenticate sensor. Can contain 50 characters.", max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    adder = forms.CharField(help_text="User, who added sensor", max_length=30, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    latest_modifier = forms.CharField(help_text="User, who has modified sensor last", max_length=30, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    software_version = forms.CharField(max_length=40, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    status = forms.ChoiceField(choices=Sensor.STATUS_CHOICES, widget=Select(attrs={'class':'form-control', 'disabled':'True'}))
    description = forms.CharField(max_length=250, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    location = forms.CharField(max_length=100, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    data_send_rate = forms.IntegerField(widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    burst_length = forms.FloatField(widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    burst_rate = forms.FloatField(widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    connection_close_limit = forms.FloatField(widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    network_close_limit = forms.FloatField(widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    update_check_limit = forms.FloatField(widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    update_url = forms.CharField(max_length=150, widget=TextInput(attrs={'class':'form-control', 'title':'Data server URL', 'disabled':'True'}))
    update_port = forms.IntegerField(widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))

    class Meta:
        model = Sensor
        fields = ['sensor_name', 'sensor_id', 'sensor_key', 'adder', 'latest_modifier', 'model', 'status', 'software_version', 'description', 'location', 'data_send_rate', 'burst_length', 'burst_rate', 'connection_close_limit', 'network_close_limit', 'update_check_limit', 'update_url', 'update_port', 'software_version', 'adder', 'latest_modifier']

class AddSensorForm(forms.ModelForm):
    sensor_name = forms.CharField(max_length=30, widget=TextInput(attrs={'class':'form-control'}))
    description = forms.CharField(max_length=250, help_text="You can give a short description for the sensor. This field is not required.", widget=TextInput(attrs={'class':'form-control'}), required=False)
    location = forms.CharField(max_length=100, help_text="The location of the sensor. This field is not required.", widget=TextInput(attrs={'class':'form-control'}), required=False)
    sensor_key = forms.CharField(max_length=50, help_text="This is the password of the sensor, which is used with sensor key to authenticate sensor. Can contain 50 characters. For example: 'RandoMGenerAtedPass345'", widget=TextInput(attrs={'class':'form-control'}), required=False)
    data_send_rate = forms.IntegerField(help_text="How often data is sent to the data server in seconds. For example value 100 means that data is sent every 100 seconds. This determines how many measurements are in one file, since each sending consist of single data file.", widget=TextInput(attrs={'class':'form-control'}), required=False, initial=10)
    burst_length = forms.FloatField(help_text="The length of burst in seconds. Use '.' as a decimal separator. 0 = continuous measurement", widget=TextInput(attrs={'class':'form-control'}), required=False, initial=0)
    burst_rate = forms.FloatField(help_text="Time between bursts in seconds. Time is measured form the end of the burst until the beginning of the next burst. For example, if burst length = 5 and burst rate = 10, the measurement takes 5 seconds and then program waits 10 second before it starts measuring again. Use '.' as a decimal separator.", widget=TextInput(attrs={'class':'form-control'}), required=False, initial=0)
    update_url = forms.CharField(help_text="The URL or IP-address of the server, where updates are fetched. Usually the same address as the address of this page. Insert the address in form: 255.255.255.255 or example.com", max_length=150, widget=TextInput(attrs={'class':'form-control'}))
    update_port = forms.IntegerField(widget=TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = Sensor
        fields = ['sensor_name', 'model', 'description', 'location', 'sensor_key', 'data_send_rate', 'burst_length', 'burst_rate', 'update_url', 'update_port']


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm password"

    username = forms.CharField(max_length=30, widget=TextInput(attrs={'class':'validate form-control form-control-lg rounded-0'}))
    first_name = forms.CharField(max_length=30, widget=TextInput(attrs={'class':'validate form-control form-control-lg rounded-0'}))
    last_name = forms.CharField(max_length=30, widget=TextInput(attrs={'class':'validate form-control form-control-lg rounded-0'}))
    email = forms.EmailField(max_length=250, widget=TextInput(attrs={'class':'validate form-control form-control-lg rounded-0'}))
    password1 = forms.CharField(max_length=30, widget=PasswordInput(attrs={'class':'validate form-control form-control-lg rounded-0', 'title':'Password'}))
    password2 = forms.CharField(max_length=30, widget=PasswordInput(attrs={'class':'validate form-control form-control-lg rounded-0', 'title':'Confirm password'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'class':'validate form-control form-control-lg rounded-0','placeholder': 'Username'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class':'form-control form-control-lg rounded-0', 'placeholder':'Password'}))

class TypeOfSensorInfoLockedForm(forms.ModelForm):
    sensor_model = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    sensor_information = forms.CharField(max_length=250, widget=Textarea(attrs={'class':'form-control', 'disabled':'True'}))

    class Meta:
        model = Type_of_sensor
        fields = ['sensor_model', 'sensor_information']

"""
class Type_of_sensorAdmin(admin.ModelAdmin):
    sensor_model = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    sensor_information = forms.CharField(max_length=250, widget=Textarea(attrs={'class':'form-control', 'disabled':'True'}))
    handle_data_function = forms.FileField(required=False, widget=ClearableFileInput())
    address = forms.IntegerField(widget=TextInput())

    class Meta:
        model = Type_of_sensor
        fields = ['sensor_model', 'sensor_information', 'handle_data_function', 'address']
"""

class ModifyWlanForm(forms.ModelForm):
    name = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control'}))
    ssid = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control'}))
    security = forms.ChoiceField(choices=Wlan.SECURITY_CHOICES, widget=Select(attrs={'class':'form-control'}))
    key = forms.CharField(help_text="Required if security is not Nothing", max_length=50, required=False, widget=TextInput(attrs={'class':'form-control'}))
    username = forms.CharField(help_text="Required if security = WPA2_ENT", max_length=50, required=False, widget=TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = Wlan
        fields = ['name', 'ssid', 'security', 'key', 'username']

class WlanInfoForm(forms.ModelForm):
    name = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    ssid = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    security = forms.ChoiceField(choices=Wlan.SECURITY_CHOICES, widget=Select(attrs={'class':'form-control', 'disabled':'True'}))
    key = forms.CharField(help_text="Required if security is not Nothing", max_length=50, required=False, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    username = forms.CharField(max_length=50, required=False, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))

    class Meta:
        model = Wlan
        fields = ['name', 'ssid', 'security', 'key', 'username']

class ModifyNbIotForm(forms.ModelForm):
    name = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control'}))
    settings = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = Nb_iot
        fields = ['name', 'settings']

class NbIotInfoForm(forms.ModelForm):
    name = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    settings = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))

    class Meta:
        model = Nb_iot
        fields = ['name', 'settings']

class ModifyHTTPForm(forms.ModelForm):
    name = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control'}))
    data_server_url = forms.CharField(max_length=150, widget=TextInput(attrs={'class':'form-control'}))
    data_server_port = forms.IntegerField(widget=TextInput(attrs={'class':'form-control'}))
    path = forms.CharField(max_length=150, widget=TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = HTTP
        fields = ['name', 'data_server_url', 'data_server_port', 'path']

class HTTPInfoForm(forms.ModelForm):
    name = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    data_server_url = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    data_server_port = forms.IntegerField(widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    path = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))

    class Meta:
        model = HTTP
        fields = ['name', 'data_server_url', 'data_server_port', 'path']

class ModifyHTTPSForm(forms.ModelForm):
    name = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control'}))
    data_server_url = forms.CharField(max_length=150, widget=TextInput(attrs={'class':'form-control'}))
    data_server_port = forms.IntegerField(widget=TextInput(attrs={'class':'form-control'}))
    path = forms.CharField(max_length=150, widget=TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = HTTPS
        fields = ['name', 'data_server_url', 'data_server_port', 'path']

class HTTPSInfoForm(forms.ModelForm):
    name = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    data_server_url = forms.CharField(max_length=150, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    data_server_port = forms.IntegerField(widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    path = forms.CharField(max_length=150, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))

    class Meta:
        model = HTTPS
        fields = ['name', 'data_server_url', 'data_server_port', 'path']


class ModifyMQTTForm(forms.ModelForm):
    name = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control'}))
    user = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control'}))
    key = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control'}))
    topic = forms.CharField(max_length=150, widget=TextInput(attrs={'class':'form-control'}))
    broker_url = forms.CharField(max_length=150, widget=TextInput(attrs={'class':'form-control'}))
    broker_port = forms.IntegerField(widget=TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = MQTT
        fields = ['name', 'user', 'key', 'topic', 'broker_url', 'broker_port']

class MQTTInfoForm(forms.ModelForm):
    name = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    user = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    key = forms.CharField(max_length=50, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    topic = forms.CharField(max_length=150, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    broker_url = forms.CharField(max_length=150, widget=TextInput(attrs={'class':'form-control', 'disabled':'True'}))
    broker_port = forms.IntegerField(widget=TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = MQTT
        fields = ['name', 'user', 'key', 'topic', 'broker_url', 'broker_port']
