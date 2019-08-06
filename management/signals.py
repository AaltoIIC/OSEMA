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
    #try:
    old_file = Type_of_sensor.objects.get(pk=instance.pk).handle_data_function
    new_file = instance.handle_data_function
    if not old_file == new_file:
        os.remove(old_file.path)
    os.rename(new_file.path, old_file.path)
    new_file.name = old_file.name
    #except:
    print("Update file couldn't be deleted. File:", instance.handle_data_function)
