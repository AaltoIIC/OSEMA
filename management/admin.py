from django.contrib import admin

from .models import User, UserAdmin, Sensor, Type_of_sensor, Value_pair, Sample_rate, Sensitivity, Wlan, Nb_iot, HTTP, HTTPS, Update, MQTT, Data_format, Variable, Default_variable
#from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Sensor)
admin.site.register(Type_of_sensor)
admin.site.register(Value_pair)
admin.site.register(Sample_rate)
admin.site.register(Sensitivity)
admin.site.register(Wlan)
admin.site.register(Nb_iot)
admin.site.register(HTTP)
admin.site.register(HTTPS)
admin.site.register(Update)
admin.site.register(MQTT)
admin.site.register(Data_format)
admin.site.register(Variable)
admin.site.register(Default_variable)
