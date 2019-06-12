from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from management.models import Update, Type_of_sensor
import os

@receiver(pre_delete, sender=Update)
def delete_update_file(sender, instance, **kwargs):
    try:
        os.remove("management/sensor_updates/" + instance.filename)
    except:
        print("Update file couldn't be deleted.")

@receiver(pre_save, sender=Type_of_sensor)
def delete_previous_file(sender, instance, **kwargs):
    try:
        print("INSTANCE", instance)
        os.remove("management/pycom_functions/handle_data_functions/" + str(instance) + ".py")
    except:
        print("Update file couldn't be deleted.")
