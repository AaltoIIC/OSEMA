from django.contrib import admin

from .models import User, UserAdmin, Sensor, Type_of_sensor, Value_pair, Sample_rate, Sensitivity, Wlan, Nb_iot, Http, Https, Update, LWDTP, MQTT
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
admin.site.register(Http)
admin.site.register(Https)
admin.site.register(Update)
admin.site.register(LWDTP)
admin.site.register(MQTT)
