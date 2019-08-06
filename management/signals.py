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
        tos = Type_of_sensor.objects.get(pk=instance.pk)
    except:
        return #object not found
    old_file = tos.handle_data_function
    new_file = instance.handle_data_function
    if old_file:
        if old_file == new_file:
            os.rename(new_file.path, old_file.path)
            new_file.name = old_file_name
        try:
            os.remove(old_file.path)
        except:
            print("Update file couldn't be deleted. File:", old_file.path)
        
