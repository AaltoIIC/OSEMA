from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse, Http404, JsonResponse

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .models import User, Sensor, Type_of_sensor, Value_pair, Sensitivity, Sample_rate, Sensor, Wlan, Nb_iot, Http, Https, Update, LWDTP, MQTT
from .forms import ModifySensorForm, ModifySensorFormLocked, AddSensorForm, SignUpForm, TypeOfSensorInfoLockedForm
from .forms import ModifyWlanForm, ModifyNbIotForm, ModifyHttpForm, ModifyHttpsForm, ModifyLWDTPForm, ModifyMQTTForm
from .forms import WlanInfoForm, NbIotInfoForm, HttpInfoForm, HttpsInfoForm, LWDTPInfoForm, MQTTInfoForm
from management.utils import update_sensor, create_new_sensor_to_dataserver, delete_sensor_from_data_server, update_sensor_status, update_key, get_latest_data_date, parse_date, get_data_files, delete_datafile_from_data_server, get_datafile, get_date_and_type, get_previous_and_next
from .api_permissions import AuthLevel2Permission
from rest_framework.decorators import api_view

from sensor_management_platform.settings import FAILURE

from rest_framework import viewsets

import datetime

import string

try:
    import secrets
    def generate_password(length):
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(length))
except:
    def generate_password(length):
        return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))



from .serializers import SensorSerializer, ModelSerializer, NbIotSerializer, WlanSerializer, HttpSerializer, LWDTPSerializer, MQTTSerializer, HttpsSerializer, SampleRateSerializer, SensitivitySerializer, ValuePairSerializer

import json
from itertools import chain

AVAILABLE_PROTOCOLS_CLASSES = [Http, Https, LWDTP, MQTT]
AVAILABLE_PROTOCOLS = ['Http', 'Https', 'LWDTP', 'MQTT']
AVAILABLE_COMMUNICATION_TECHNOLOGIES_CLASSES = [Wlan, Nb_iot]
AVAILABLE_COMMUNICATION_TECHNOLOGIES = ['Wlan', 'Nb_iot']

"""API"""
class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [AuthLevel2Permission]

class ModelViewSet(viewsets.ModelViewSet):
    queryset = Type_of_sensor.objects.all()
    serializer_class = ModelSerializer
    permission_classes = [AuthLevel2Permission]

class NbIotViewSet(viewsets.ModelViewSet):
    queryset = Nb_iot.objects.all()
    serializer_class = NbIotSerializer
    permission_classes = [AuthLevel2Permission]

class WlanViewSet(viewsets.ModelViewSet):
    queryset = Wlan.objects.all()
    serializer_class = WlanSerializer
    permission_classes = [AuthLevel2Permission]

class HttpViewSet(viewsets.ModelViewSet):
    queryset = Http.objects.all()
    serializer_class = HttpSerializer
    permission_classes = [AuthLevel2Permission]

class HttpsViewSet(viewsets.ModelViewSet):
    queryset = Https.objects.all()
    serializer_class = HttpsSerializer
    permission_classes = [AuthLevel2Permission]

class LWDTPViewSet(viewsets.ModelViewSet):
    queryset = LWDTP.objects.all()
    serializer_class = LWDTPSerializer
    permission_classes = [AuthLevel2Permission]

class MQTTViewSet(viewsets.ModelViewSet):
    queryset = MQTT.objects.all()
    serializer_class = MQTTSerializer
    permission_classes = [AuthLevel2Permission]

class SampleRateViewSet(viewsets.ModelViewSet):
    queryset = Sample_rate.objects.all()
    serializer_class = SampleRateSerializer
    permission_classes = [AuthLevel2Permission]

class SensitivityViewSet(viewsets.ModelViewSet):
    queryset = Sensitivity.objects.all()
    serializer_class = SensitivitySerializer
    permission_classes = [AuthLevel2Permission]

class ValuePairViewSet(viewsets.ModelViewSet):
    queryset = Value_pair.objects.all()
    serializer_class = ValuePairSerializer
    permission_classes = [AuthLevel2Permission]

@api_view(['POST'])
def get_update(request):
    if request.method == 'POST':
        sensor_object = get_object_or_404(Sensor, pk=request.POST['sensor_id'])
        sensor_object.software_version = request.POST['software_version']
        if sensor_object.sensor_key == request.POST['sensor_key']:
            update = Update.objects.filter(sensor=sensor_object).order_by('-date')[0]
            if update.filename != request.POST['software_version']:
                with open('management/sensor_updates/' + update.filename, 'r') as f:
                    content = f.read()
                    return HttpResponse(content, content_type='text/plain')
            elif update.filename == request.POST['software_version']:
                print("sensor_id", sensor_object.sensor_id,"status", sensor_object.status)
                if sensor_object.status != Sensor.MEASURING_UP_TO_DATE:
                    sensor_object.software_version = update.filename
                    sensor_object.status = Sensor.MEASURING_UP_TO_DATE
                    sensor_object.save()
                    update_sensor_status(sensor_object, Sensor.MEASURING_UP_TO_DATE)
                return HttpResponse("UP-TO-DATE", content_type='text/plain')
        elif sensor_object.sensor_key_old == request.POST['sensor_key']:
            update = Update.objects.filter(sensor=sensor_object).order_by('-date')[0]
            with open('management/sensor_updates/' + update.filename, 'r') as f:
                content = f.read()
                return HttpResponse(content, content_type='text/plain')
        raise Http404("Page doesn't exist")

@api_view(['POST'])
def confirm_update(request):
    if request.method == 'POST':
        sensor_object = get_object_or_404(Sensor, pk=request.POST['sensor_id'])
        if sensor_object.sensor_key == request.POST['sensor_key']:
            sensor_object.status = Sensor.MEASURING_UP_TO_DATE
            update_sensor_status(sensor_object, Sensor.MEASURING_UP_TO_DATE)
            sensor_object.save()
            return HttpResponse("OK", content_type='text/plain')
        elif sensor_object.sensor_key_old == request.POST['sensor_key']:
            alphabet = string.ascii_letters + string.digits
            sensor_object.sensor_key_old = ''.join(generate_password(20)) #generate random 20-character alphanumeric password
            sensor_object.status = Sensor.MEASURING_UP_TO_DATE
            update_key(sensor_object)
            update_sensor_status(sensor_object, Sensor.MEASURING_UP_TO_DATE)
            sensor_object.save()
            return HttpResponse("OK", content_type='text/plain')
        else:
            raise Http404("Page doesn't exist")
    else:
        raise Http404("Page doesn't exist")

@api_view(['POST'])
def failure(request):
    sensor_object = get_object_or_404(Sensor, pk=request.POST['sensor_id'])
    if sensor_object.sensor_key == request.POST['sensor_key']:
        print("Status", request.POST['status'])
        if request.POST['status'] == "OSError":
            sensor_object.status = Sensor.FAILURE_OS
        elif request.POST['status'] == "MemoryError":
            sensor_object.status = Sensor.FAILURE_MEM
        elif request.POST['status'] == "I2CError":
            sensor_object.status = Sensor.FAILURE_I2C
        sensor_object.save()
        return HttpResponse("OK", content_type='text/plain')
    else:
        raise Http404("Page doesn't exist")


#main page
def index(request):
    return render(request, 'management/index.html')

#if one doesn't click dropdown menu
@login_required
def sensors(request):
    return render(request, 'management/sensors.html')

#add sensor
@login_required
def add_sensor(request):
    user = request.user
    errors_sensor_form = False
    errors = False
    if request.method == 'POST':
        if user.auth_level < 2:
            context = {'title':'Not authorized!', 'error_msg':'You are not allowed to add sensors. Please contact admin to request rights to modify/add sensors.'}
            return render(request, 'management/error.html', context)
        else:
            add_sensor_form = AddSensorForm(request.POST, prefix='add_sensor')
            communication_technology = request.POST['communication_technology']
            protocol = request.POST['protocol']
            if add_sensor_form.is_valid():
                new_sensor = add_sensor_form.save()
                new_sensor.sample_rate = Sample_rate.objects.get(id=request.POST['add_sensor-sample_rate'])
                new_sensor.sensitivity = Sensitivity.objects.get(id=request.POST['add_sensor-sensitivity'])
                if communication_technology ==  'Wlan':
                    instance = Wlan.objects.get(pk=request.POST['communication_instance'])
                    modified_wlan_form = ModifyWlanForm(request.POST, instance=instance, prefix='wlan')
                    communication_instances = Wlan.objects.all()
                    modify_communication_form = modified_wlan_form
                    if modified_wlan_form.is_valid():
                        modified_wlan_form.save()
                        new_sensor.communication_object = instance
                    else:
                        errors = True
                elif communication_technology == 'Nb_iot':
                    instance = Nb_iot.objects.get(pk=request.POST['communication_instance'])
                    modified_nb_iot_form = ModifyNbIotForm(request.POST, instance=instance, prefix='nb_iot')
                    communication_instances = Nb_iot.objects.all()
                    modify_communication_form = modified_nb_iot_form
                    if modified_nb_iot_form.is_valid():
                        modified_nb_iot_form.save()
                        new_sensor.communication_object = instance
                    else:
                        errors = True
                if protocol == 'Http':
                    instance = Http.objects.get(pk=request.POST['protocol_instance'])
                    modified_http_form = ModifyHttpForm(request.POST, instance=instance, prefix='http')
                    protocol_instances = Http.objects.all()
                    modify_protocol_form = modified_http_form
                    if modified_http_form.is_valid():
                        modified_http_form.save()
                        new_sensor.protocol_object = instance
                    else:
                        errors = True
                elif protocol == 'Https':
                    instance = Https.objects.get(pk=request.POST['protocol_instance'])
                    modified_https_form = ModifyHttpsForm(request.POST, instance=instance, prefix='https')
                    protocol_instances = Https.objects.all()
                    modify_protocol_form = modified_https_form
                    if modified_https_form.is_valid():
                        modified_https_form.save()
                        new_sensor.protocol_object = instance
                    else:
                        errors = True
                elif protocol == 'LWDTP':
                    instance = LWDTP.objects.get(pk=request.POST['protocol_instance'])
                    modified_LWDTP_form = ModifyLWDTPForm(request.POST, instance=instance, prefix='lwdtp')
                    lwdtp_instances = LWDTP.objects.all()
                    modify_protocol_form = modified_LWDTP_form
                    if modified_LWDTP_form.is_valid():
                        modified_LWDTP_form.save()
                        new_sensor.protocol_object = instance
                    else:
                        errors = True
                elif protocol == 'MQTT':
                    instance = MQTT.objects.get(pk=request.POST['protocol_instance'])
                    modified_MQTT_form = ModifyMQTTForm(request.POST, instance=instance, prefix='mqtt')
                    mqtt_instances = MQTT.objects.all()
                    modify_protocol_form = modified_MQTT_form
                    if modified_MQTT_form.is_valid():
                        modified_MQTT_form.save()
                        new_sensor.protocol_object = instance
                    else:
                        errors = True
                if not errors:
                    new_sensor.status = Sensor.WAITING_FOR_UPDATE
                    new_sensor.adder = user
                    new_sensor.latest_modifier = user
                    new_sensor.save()
                    create_new_sensor_to_dataserver(new_sensor)
                    return redirect('browse_sensors')

                else:
                    new_sensor.delete()
            else:
                errors_sensor_form = True
    #If not post fill the form
    #Give initial values
    found = False
    for communication_type_class in AVAILABLE_COMMUNICATION_TECHNOLOGIES_CLASSES:
        if communication_type_class.objects.all().exists():
            found = True
            communication_object = communication_type_class.objects.all()[0]
            communication_type = communication_object.__class__.__name__
            break
    if not found:
        context = {'title':'You need to create communication object!', 'error_msg':'You need to create communication object before adding new sensors.'}
        return render(request, 'configurator/error.html', context)
    found = False
    for protocol_type_class in AVAILABLE_PROTOCOLS_CLASSES:
        if protocol_type_class.objects.all().exists():
            found = True
            protocol_object = protocol_type_class.objects.all()[0]
            protocol = protocol_object.__class__.__name__
            break
    if not found:
        context = {'title':'You need to add application layer protocol objects!', 'error_msg':'You need to create application layer protocol object before adding sensor.'}
        return render(request, 'configurator/error.html', context)
    if not Type_of_sensor.objects.all().exists():
        context = {'title':'Not authorized!', 'error_msg':'You are not allowed to add sensor. Please contact admin to request rights to modify/add sensors.'}
        return render(request, 'configurator/error.html', context)
    initial_sensor_type = Type_of_sensor.objects.all()[0]
    available_sample_rates = Sample_rate.objects.filter(model=initial_sensor_type.pk)
    initial_sample_rate = available_sample_rates[0]
    available_sensitivities = initial_sample_rate.supported_sensitivities.all()
    initial_sensitivity = available_sensitivities[0]
    if user.auth_level >= 2:
        if not errors_sensor_form:
            add_sensor_form = AddSensorForm(prefix='add_sensor')
        if not errors:
            modify_communication_form = ModifyWlanForm(instance=communication_object, prefix='wlan')
            communication_instances = Wlan.objects.all()
            modify_protocol_form = ModifyLWDTPForm(instance=protocol_object, prefix='lwdtp')
            protocol_instances = LWDTP.objects.all()
    else:
        context = {'title':'Not authorized!', 'error_msg':'You are not allowed to add sensor. Please contact admin to request rights to modify/add sensors.'}
        return render(request, 'management/error.html', context)
    context =   {'add_sensor_form' : add_sensor_form,
                'available_sample_rates': available_sample_rates,
                'current_sample_rate': initial_sample_rate.id,
                'available_sensitivities': available_sensitivities,
                'current_sensitivity': initial_sensitivity.id,
                'current_communication_technology': communication_object.__class__.__name__,
                'current_communication_id': communication_object.id,
                'communication_instances': communication_instances,
                'modify_communication_form': modify_communication_form,
                'available_communication_technologies': AVAILABLE_COMMUNICATION_TECHNOLOGIES,
                'current_protocol': protocol_object.__class__.__name__,
                'current_protocol_id': protocol_object.id,
                'protocol_instances': protocol_instances,
                'modify_protocol_form': modify_protocol_form,
                'available_protocols': AVAILABLE_PROTOCOLS
    }
    return render(request, 'management/add_sensor.html', context)

#browse sensors
@login_required
def browse_sensors(request):
    context = {}
    sensors = list(map(lambda x: {"name":x.sensor_name, "location":x.location, "status":x.get_status_display(),
                                "model":x.model.sensor_model, "date_added":x.date_added, "date_modified":x.date_modified, "id":x.pk},
                                Sensor.objects.all()))
    context['sensors'] = sensors
    return render(request, 'management/browse_sensors.html', context)

@login_required
def sensor_info(request, sensor_id):
    sensor = Sensor.objects.get(pk=sensor_id)
    sensor_form = ModifySensorFormLocked(instance=sensor)
    communication_object = sensor.communication_object
    communication_type = communication_object.__class__.__name__
    protocol_object = sensor.protocol_object
    protocol = protocol_object.__class__.__name__
    if communication_type == 'Wlan':
        communication_form = WlanInfoForm(instance=communication_object, prefix='wlan')
    elif communication_type == 'Nb_iot':
        communication_form = NbIotInfoForm(instance=communication_object, prefix='nb_iot')
    else:
        raise Http404("Page doesn't exist")
    if protocol == 'Http':
        protocol_form = HttpInfoForm(instance=protocol_object, prefix='http')
    elif protocol == 'Https':
        protocol_form = HttpsInfoForm(instance=protocol_object, prefix='https')
    elif protocol == 'LWDTP':
        protocol_form = LWDTPInfoForm(instance=protocol_object, prefix='lwdtp')
    elif protocol == 'MQTT':
        protocol_form = MQTTInfoForm(instance=protocol_object, prefix='mqtt')
    else:
        raise Http404("Page doesn't exist")
    latest_modifier = sensor.latest_modifier
    adder = sensor.adder
    context =   {'sensor_form' : sensor_form,
                'current_sample_rate': sensor.sample_rate.sample_rate,
                'current_sensitivity': sensor.sensitivity.sensitivity,
                'adder' : adder,
                'latest_modifier' : latest_modifier,
                'communication_technology' : communication_type,
                'communication_form' : communication_form,
                'protocol_form': protocol_form,
                'sensor_id': sensor_id,
                'protocol' : protocol
    }
    return render(request, 'management/sensor_info.html', context)

@login_required
def return_software_file(request, sensor_id):
    if request.user.auth_level > 1:
        sensor_object = get_object_or_404(Sensor, pk=sensor_id)
        update = Update.objects.filter(sensor=sensor_object).order_by('-date')[0]
        with open('management/sensor_updates/' + update.filename, 'r') as f:
            content = f.read()
            response = HttpResponse(content, content_type='text/x-python')
            response['Content-Disposition'] = 'attachment; filename={0}'.format("main.py")
            return response
    else:
        return render(request, 'management/error.html', {'title' : 'Not authorized', 'error_msg' : 'Ask rights to download sensor from admin.'})

@login_required
def modify_sensor(request, sensor_id):
    errors = False
    user = request.user
    if request.method == 'POST':
        if user.auth_level < 2:
            context = {'title':'Not authorized!', 'error_msg':'You are not allowed to modify sensor values. Please contact admin to request rights to modify/add sensors.'}
            return render(request, 'management/error.html', context)
        else:
            modified_sensor = Sensor.objects.get(pk=sensor_id)
            modified_sensor_form = ModifySensorForm(request.POST, instance=modified_sensor, prefix='modify_sensor')
            communication_technology = request.POST['communication_technology']
            protocol = request.POST['protocol']
            if communication_technology ==  'Wlan':
                instance = Wlan.objects.get(pk=request.POST['communication_instance'])
                modified_wlan_form = ModifyWlanForm(request.POST, instance=instance, prefix='wlan')
                communication_instances = Wlan.objects.all()
                modify_communication_form = modified_wlan_form
                if modified_wlan_form.is_valid():
                    modified_wlan_form.save()
                    modified_sensor.communication_object = instance
                else:
                    errors = True
            elif communication_technology == 'Nb_iot':
                instance = Nb_iot.objects.get(pk=request.POST['communication_instance'])
                modified_nb_iot_form = ModifyNbIotForm(request.POST, instance=instance, prefix='nb_iot')
                communication_instances = Nb_iot.objects.all()
                modify_communication_form = modified_nb_iot_form
                if modified_nb_iot_form.is_valid():
                    modified_nb_iot_form.save()
                    modified_sensor.communication_object = instance
                else:
                    errors = True
            if protocol == 'Http':
                instance = Http.objects.get(pk=request.POST['protocol_instance'])
                modified_http_form = ModifyHttpForm(request.POST, instance=instance, prefix='http')
                protocol_instances = Http.objects.all()
                modify_protocol_form = modified_http_form
                if modified_http_form.is_valid():
                    modified_http_form.save()
                    modified_sensor.protocol_object = instance
                else:
                    errors = True
            elif protocol == 'Https':
                instance = Https.objects.get(pk=request.POST['protocol_instance'])
                modified_https_form = ModifyHttpsForm(request.POST, instance=instance, prefix='https')
                protocol_instances = Https.objects.all()
                modify_protocol_form = modified_https_form
                if modified_https_form.is_valid():
                    modified_https_form.save()
                    modified_sensor.protocol_object = instance
                else:
                    errors = True
            elif protocol == 'LWDTP':
                instance = LWDTP.objects.get(pk=request.POST['protocol_instance'])
                modified_LWDTP_form = ModifyLWDTPForm(request.POST, instance=instance, prefix='lwdtp')
                protocol_instances = LWDTP.objects.all()
                modify_protocol_form = modified_LWDTP_form
                if modified_LWDTP_form.is_valid():
                    modified_LWDTP_form.save()
                    modified_sensor.protocol_object = instance
                else:
                    errors = True
            elif protocol == 'MQTT':
                instance = MQTT.objects.get(pk=request.POST['protocol_instance'])
                modified_MQTT_form = ModifyMQTTForm(request.POST, instance=instance, prefix='mqtt')
                protocol_instances = MQTT.objects.all()
                modify_protocol_form = modified_MQTT_form
                if modified_MQTT_form.is_valid():
                    modified_MQTT_form.save()
                    modified_sensor.protocol_object = instance
                else:
                    errors = True
            old_key = modified_sensor.sensor_key
            modify_sensor_form = modified_sensor_form
            if modified_sensor_form.is_valid():
                if not errors:
                    modified_sensor.sample_rate = Sample_rate.objects.get(id=request.POST['modify_sensor-sample_rate'])
                    modified_sensor.sensitivity = Sensitivity.objects.get(id=request.POST['modify_sensor-sensitivity'])
                    if old_key != request.POST['modify_sensor-sensor_key']:
                        modified_sensor.sensor_key_old = old_key
                    modified_sensor_form.save()
                    if modified_sensor.status != Sensor.WAITING_FOR_UPDATE:
                        print("meni tanne vaikkei pitanyt")
                        modified_sensor.status = Sensor.MEASURING_WAITING_FOR_UPDATE
                    modified_sensor.latest_modifier = user
                    modified_sensor.date_modified = datetime.datetime.now()
                    modified_sensor.save()
                    update_sensor(modified_sensor)
                    return redirect('browse_sensors')
            else:
                errors = True
    #If not post fill the form
    sensor = Sensor.objects.get(pk=sensor_id)
    communication_object = sensor.communication_object
    communication_type = communication_object.__class__.__name__
    protocol_object = sensor.protocol_object
    protocol = protocol_object.__class__.__name__
    if user.auth_level >= 2:
        if not errors:
            modify_sensor_form = ModifySensorForm(instance=sensor, prefix='modify_sensor')
            if communication_type == 'Wlan':
                modify_communication_form = ModifyWlanForm(instance=communication_object, prefix='wlan')
                communication_instances = Wlan.objects.all()
            elif communication_type == 'Nb_iot':
                modify_communication_form = ModifyNbIotForm(instance=communication_object, prefix='nb_iot')
                communication_instances = Nb_iot.objects.all()
            else:
                raise Http404("Page doesn't exist")
            if protocol == 'Http':
                modify_protocol_form = ModifyHttpForm(instance=protocol_object, prefix='http')
                protocol_instances = Http.objects.all()
            elif protocol == 'Https':
                modify_protocol_form = ModifyHttpsForm(instance=protocol_object, prefix='https')
                protocol_instances = Https.objects.all()
            elif protocol == 'LWDTP':
                modify_protocol_form = ModifyLWDTPForm(instance=protocol_object, prefix='lwdtp')
                protocol_instances = LWDTP.objects.all()
            elif protocol == 'MQTT':
                modify_protocol_form = ModifyMQTTForm(instance=protocol_object, prefix='mqtt')
                protocol_instances = MQTT.objects.all()
            else:
                raise Http404("Page doesn't exist")
    else:
        return render(request, 'management/error.html', {'title' : 'You are not allowed to modify sensor', 'error_msg' : 'Ask rights to modify sensor from admin.'})

    available_sample_rates = Sample_rate.objects.filter(model=sensor.model.pk)
    available_sensitivities = sensor.sample_rate.supported_sensitivities.all()
    context =   {'modify_sensor_form' : modify_sensor_form,
                'available_sample_rates': available_sample_rates,
                'current_sample_rate': sensor.sample_rate.id,
                'available_sensitivities': available_sensitivities,
                'current_sensitivity': sensor.sensitivity.id,
                'current_communication_technology': sensor.communication_object.__class__.__name__,
                'current_communication_id': sensor.communication_object.id,
                'communication_instances': communication_instances,
                'modify_communication_form': modify_communication_form,
                'available_communication_technologies':AVAILABLE_COMMUNICATION_TECHNOLOGIES,
                'current_protocol': sensor.protocol_object.__class__.__name__,
                'current_protocol_id': sensor.protocol_object.id,
                'protocol_instances': protocol_instances,
                'modify_protocol_form': modify_protocol_form,
                'available_protocols': AVAILABLE_PROTOCOLS
    }
    return render(request, 'management/modify_sensor.html', context)

"""Used to get list of available sample rates to certain type of sensor. Used by ajax"""
@login_required
def get_available_sample_rates(request, sensor_model):
    sensor_model_obj = get_object_or_404(Type_of_sensor, pk=sensor_model)
    available_sample_rates = Sample_rate.objects.filter(model=sensor_model)
    rate_dict = {}
    for rate in available_sample_rates:
        rate_dict[rate.id] = rate.sample_rate
    return JsonResponse(json.dumps(rate_dict), safe=False)

"""Used to get list of available sample rates to certain type of sensor. Used by ajax"""
@login_required
def get_available_sensitivities(request, sample_rate_id):
    sample_rate_obj = get_object_or_404(Sample_rate, pk=sample_rate_id)
    supported_sensitivities = sample_rate_obj.supported_sensitivities.all()
    sensitivity_dict = {}
    for sensitivity in supported_sensitivities:
        sensitivity_dict[sensitivity.id] = sensitivity.sensitivity
    return JsonResponse(json.dumps(sensitivity_dict), safe=False)

@login_required
def get_communication_instances(request, type):
    if type == "Wlan":
        instances = Wlan.objects.all()
    elif type == "Nb_iot":
        instances = Nb_iot.objects.all()
    else:
        raise Http404("Page doesn't exist")
    instance_dict = {}
    for instance in instances:
        instance_dict[instance.id] = instance.name
    return JsonResponse(json.dumps(instance_dict), safe=False)

@login_required
def get_protocol_instances(request, type):
    if type == "Http":
        instances = Http.objects.all()
    elif type == "Https":
        instances = Https.objects.all()
    elif type == "LWDTP":
        instances = LWDTP.objects.all()
    elif type == "MQTT":
        instances = MQTT.objects.all()
    else:
        raise Http404("Page doesn't exist")
    instance_dict = {}
    for instance in instances:
        instance_dict[instance.id] = instance.name
    return JsonResponse(json.dumps(instance_dict), safe=False)

@login_required
def get_communication_technology_form(request, type, id):
    if type == 'Wlan':
        communication_object = get_object_or_404(Wlan, pk=id)
        modify_communication_form = ModifyWlanForm(instance=communication_object, prefix='wlan')
    elif type == 'Nb_iot':
        communication_object = get_object_or_404(Nb_iot, pk=id)
        modify_communication_form = ModifyNbIotForm(instance=communication_object, prefix='nb_iot')
    else:
        raise Http404("Page doesn't exist")
    return JsonResponse(json.dumps(modify_communication_form.as_table()), safe=False)

@login_required
def get_communication_technology_form_blank(request, type):
    if type == 'Wlan':
        modify_communication_form = ModifyWlanForm(prefix='wlan')
    elif type == 'Nb_iot':
        modify_communication_form = ModifyNbIotForm(prefix='nb_iot')
    else:
        raise Http404("Page doesn't exist")
    return JsonResponse(json.dumps(modify_communication_form.as_table()), safe=False)

@login_required
def get_protocol_form(request, type, id):
    if type == 'Http':
        protocol_object = get_object_or_404(Http, pk=id)
        modify_protocol_form = ModifyHttpForm(instance=protocol_object, prefix='http')
    elif type == 'Https':
        protocol_object = get_object_or_404(Https, pk=id)
        modify_protocol_form = ModifyHttpsForm(instance=protocol_object, prefix='https')
    elif type == 'LWDTP':
        protocol_object = get_object_or_404(LWDTP, pk=id)
        modify_protocol_form = ModifyLWDTPForm(instance=protocol_object, prefix='lwdtp')
    elif type == 'MQTT':
        protocol_object = get_object_or_404(MQTT, pk=id)
        modify_protocol_form = ModifyMQTTForm(instance=protocol_object, prefix='mqtt')
    else:
        raise Http404("Page doesn't exist")
    return JsonResponse(json.dumps(modify_protocol_form.as_table()), safe=False)

@login_required
def get_protocol_form_blank(request, type):
    if type == 'Http':
        modify_protocol_form = ModifyHttpForm(prefix='http')
    elif type == 'Https':
        modify_protocol_form = ModifyHttpsForm(prefix='https')
    elif type == 'LWDTP':
        modify_protocol_form = ModifyLWDTPForm(prefix='lwdtp')
    elif type == 'MQTT':
        modify_protocol_form = ModifyMQTTForm(prefix='mqtt')
    else:
        raise Http404("Page doesn't exist")
    return JsonResponse(json.dumps(modify_protocol_form.as_table()), safe=False)

@login_required
def delete_sensor(request, sensor_id):
    sensor_object = Sensor.objects.get(pk=sensor_id)
    delete_sensor_from_data_server(sensor_object)
    sensor_object.delete()
    return redirect('browse_sensors')

@login_required
def sensor_type_info(request, model):
    sensor_model = Type_of_sensor.objects.get(sensor_model=model)
    sensor_form = TypeOfSensorInfoLockedForm(instance=sensor_model)
    context = {'form' : sensor_form}
    return render(request, 'management/sensor_type_info.html', context)

@login_required
def communication_technologies(request):
    return render(request, 'management/communication_technologies.html')

@login_required
def browse_communication_technologies(request):
    context = {}
    wlans = list(map(lambda x: {"name":x.name, 'type':x.__class__.__name__, "id":x.pk},
                                Wlan.objects.all()))
    nb_iots = list(map(lambda x: {"name":x.name, 'type':x.__class__.__name__, "id":x.pk},
                                Nb_iot.objects.all()))
    context['wlans'] = wlans
    context['nb_iots'] = nb_iots
    return render(request, 'management/browse_communication_technologies.html', context)

@login_required
def add_communication_technologies(request):
    user = request.user
    if request.method == 'POST':
        if user.auth_level < 2:
            context = {'title':'Not authorized!', 'error_msg':'You are not allowed to add new instances. Please contact admin to request rights to modify/add instances.'}
            return render(request, 'management/error.html', context)
        else:
            communication_technology = request.POST['communication_technology']
            if communication_technology ==  'Wlan':
                modified_wlan_form = ModifyWlanForm(request.POST, prefix='wlan')
                if modified_wlan_form.is_valid():
                    modified_wlan_form.save()
            elif communication_technology == 'Nb_iot':
                modified_nb_iot_form = ModifyNbIotForm(request.POST, prefix='nb_iot')
                if modified_nb_iot_form.is_valid():
                    modified_nb_iot_form.save()
            return redirect('browse_communication_technologies')
    context =   {'available_communication_technologies': AVAILABLE_COMMUNICATION_TECHNOLOGIES,
                'communication_form': ModifyWlanForm(prefix='wlan')
    }
    return render(request, 'management/add_communication_technology.html', context)

@login_required
def modify_communication_technologies(request, type, id):
    user = request.user
    if request.method == 'POST':
        if user.auth_level < 2:
            context = {'title':'Not authorized!', 'error_msg':'You are not allowed to modify communication technology instances. Please contact admin to request rights to modify/add communication technology instances.'}
            return render(request, 'management/error.html', context)
        else:
            if type == 'Wlan':
                communication_object = get_object_or_404(Wlan, pk=id)
                modify_communication_form = ModifyWlanForm(request.POST, instance=communication_object, prefix='wlan')
            elif type == 'Nb_iot':
                communication_object = get_object_or_404(Nb_iot, pk=id)
                modify_communication_form = ModifyNbIotForm(request.POST, instance=communication_object, prefix='nb_iot')
            else:
                raise Http404("Page doesn't exist")
            if modify_communication_form.is_valid():
                modify_communication_form.save()
                return redirect('browse_communication_technologies')
    if user.auth_level >= 2:
        if type == 'Wlan':
            communication_object = get_object_or_404(Wlan, pk=id)
            form = ModifyWlanForm(instance=communication_object, prefix='wlan')
        elif type == 'Nb_iot':
            communication_object = get_object_or_404(Nb_iot, pk=id)
            form = ModifyNbIotForm(instance=communication_object, prefix='nb_iot')
        else:
            raise Http404("Page doesn't exist")
    else:
        if type == 'Wlan':
            communication_object = get_object_or_404(Wlan, pk=id)
            form = WlanInfoForm(instance=communication_object, prefix='wlan')
        elif type == 'Nb_iot':
            communication_object = get_object_or_404(Nb_iot, pk=id)
            form = NbIotInfoForm(instance=communication_object, prefix='nb_iot')
        else:
            raise Http404("Page doesn't exist")
    return render(request, 'management/modify_communication_technology.html', {'form': form})

@login_required
def delete_communication_technologies(request, type, id):
    if type == 'Wlan':
        Wlan.objects.filter(pk=id).delete()
    elif type == 'Nb_iot':
        Nb_iot.objects.filter(pk=id).delete()
    else:
        raise Http404("Page doesn't exist")
    return redirect('browse_communication_technologies')

@login_required
def communication_technologies_info(request, type, id):
    if type == 'Wlan':
        communication_object = get_object_or_404(Wlan, pk=id)
        form = WlanInfoForm(instance=communication_object)
    elif type == 'Nb_iot':
        communication_object = get_object_or_404(Nb_iot, pk=id)
        form = NbIotInfoForm(instance=communication_object)
    else:
        raise Http404("Page doesn't exist")
    context = {'form' : form}
    return render(request, 'management/communication_technology_info.html', context)

@login_required
def protocols(request):
    return render(request, 'management/protocols.html')

@login_required
def protocol_info(request, type, id):
    if type == 'Http':
        communication_object = get_object_or_404(Http, pk=id)
        form = HttpInfoForm(instance=communication_object)
    elif type == 'Https':
        communication_object = get_object_or_404(Https, pk=id)
        form = HttpsInfoForm(instance=communication_object)
    elif type == 'LWDTP':
        communication_object = get_object_or_404(LWDTP, pk=id)
        form = LWDTPInfoForm(instance=communication_object)
    elif type == 'MQTT':
        communication_object = get_object_or_404(MQTT, pk=id)
        form = MQTTInfoForm(instance=communication_object)
    else:
        raise Http404("Page doesn't exist")
    context = {'form' : form}
    return render(request, 'management/protocol_info.html', context)

@login_required
def browse_protocols(request):
    context = {}
    http_instances = list(map(lambda x: {"name":x.name, 'type':x.__class__.__name__, "id":x.pk},
                                Http.objects.all()))
    https_instances = list(map(lambda x: {"name":x.name, 'type':x.__class__.__name__, "id":x.pk},
                                Https.objects.all()))
    lwdtp_instances = list(map(lambda x: {"name":x.name, 'type':x.__class__.__name__, "id":x.pk},
                                LWDTP.objects.all()))
    mqtt_instances = list(map(lambda x: {"name":x.name, 'type':x.__class__.__name__, "id":x.pk},
                                MQTT.objects.all()))
    context['http_instances'] = http_instances
    context['https_instances'] = https_instances
    context['lwdtp_instances'] = lwdtp_instances
    context['mqtt_instances'] = mqtt_instances
    return render(request, 'management/browse_protocols.html', context)

@login_required
def add_protocols(request):
    user = request.user
    if request.method == 'POST':
        if user.auth_level < 2:
            context = {'title':'Not authorized!', 'error_msg':'You are not allowed to add new instances. Please contact admin to request rights to modify/add instances.'}
            return render(request, 'management/error.html', context)
        else:
            protocol = request.POST['protocol']
            if protocol ==  'Http':
                modified_form = ModifyHttpForm(request.POST, prefix='http')
            elif protocol == 'Https':
                modified_form = ModifyHttpsForm(request.POST, prefix='https')
            elif protocol == 'LWDTP':
                modified_form = ModifyLWDTPForm(request.POST, prefix='lwdtp')
            elif protocol == 'MQTT':
                modified_form = ModifyMQTTForm(request.POST, prefix='mqtt')
            else:
                raise Http404("Page doesn't exist")
            if modified_form.is_valid():
                modified_form.save()
            return redirect('browse_protocols')
    context =   {'available_protocols': AVAILABLE_PROTOCOLS,
                'protocol_form': ModifyLWDTPForm(prefix='lwdtp'),
                'initial_protocol': 'LWDTP'
    }
    return render(request, 'management/add_protocol.html', context)

@login_required
def modify_protocols(request, type, id):
    user = request.user
    if request.method == 'POST':
        if user.auth_level < 2:
            context = {'title':'Not authorized!', 'error_msg':'You are not allowed to modify protocol instances. Please contact admin to request rights to modify/add protocol instances.'}
            return render(request, 'management/error.html', context)
        else:
            if type == 'Http':
                protocol_object = get_object_or_404(Http, pk=id)
                modify_protocol_form = ModifyHttpForm(request.POST, instance=protocol_object, prefix='http')
            elif type == 'Https':
                protocol_object = get_object_or_404(Https, pk=id)
                modify_protocol_form = ModifyHttpsForm(request.POST, instance=protocol_object, prefix='https')
            elif type == 'LWDTP':
                protocol_object = get_object_or_404(LWDTP, pk=id)
                modify_protocol_form = ModifyLWDTPForm(request.POST, instance=protocol_object, prefix='lwdtp')
            elif type == 'MQTT':
                protocol_object = get_object_or_404(MQTT, pk=id)
                modify_protocol_form = ModifyMQTTForm(request.POST, instance=protocol_object, prefix='mqtt')
            else:
                raise Http404("Page doesn't exist")
            if modify_protocol_form.is_valid():
                modify_protocol_form.save()
                return redirect('browse_protocols')
    if user.auth_level >= 2:
        if type == 'Http':
            protocol_object = get_object_or_404(Http, pk=id)
            form = ModifyHttpForm(instance=protocol_object, prefix='http')
        elif type == 'Https':
            protocol_object = get_object_or_404(Https, pk=id)
            form = ModifyHttpsForm(instance=protocol_object, prefix='https')
        elif type == 'LWDTP':
            protocol_object = get_object_or_404(LWDTP, pk=id)
            form = ModifyLWDTPForm(instance=protocol_object, prefix='lwdtp')
        elif type == 'MQTT':
            protocol_object = get_object_or_404(MQTT, pk=id)
            form = ModifyMQTTForm(instance=protocol_object, prefix='mqtt')
        else:
            raise Http404("Page doesn't exist")
    else:
        if type == 'Http':
            protocol_object = get_object_or_404(Http, pk=id)
            form = HttpInfoForm(instance=protocol_object, prefix='http')
        elif type == 'Https':
            protocol_object = get_object_or_404(Https, pk=id)
            form = HttpsInfoForm(instance=protocol_object, prefix='https')
        elif type == 'LWDTP':
            protocol_object = get_object_or_404(LWDTP, pk=id)
            form = LWDTPInfoForm(instance=protocol_object, prefix='lwdtp')
        elif type == 'MQTT':
            protocol_object = get_object_or_404(MQTT, pk=id)
            form = MQTTInfoForm(instance=protocol_object, prefix='mqtt')
        else:
            raise Http404("Page doesn't exist")
    return render(request, 'management/modify_protocol.html', {'form': form})

@login_required
def delete_protocols(request, type, id):
    if type == 'Http':
        Http.objects.filter(pk=id).delete()
    elif type == 'Https':
        Https.objects.filter(pk=id).delete()
    elif type == 'LWDTP':
        LWDTP.objects.filter(pk=id).delete()
    elif type == 'MQTT':
        MQTT.objects.filter(pk=id).delete()
    else:
        raise Http404("Page doesn't exist")
    return redirect('browse_protocols')

#list all sensors data
@login_required
def data(request):
    checked_addresses = []
    sensor_data_dates = {}
    for sensor in Sensor.objects.all():
        if sensor.data_server_ip_address not in checked_addresses:
            data = get_latest_data_date(sensor)
            if data != FAILURE:
                data_as_json = data.json()
                data_as_dict = dict(data_as_json)
                sensor_data_dates.update(data_as_dict)
                checked_addresses.append(sensor.data_server_ip_address)
    for sensor in Sensor.objects.all():
        try:
            value = sensor_data_dates[str(sensor.sensor_id)]
        except KeyError:
            sensor_data_dates[str(sensor.sensor_id)] = ["Not available", "None", "Not available"]
    context = {}
    sensors = list(map(lambda x: {  "name":x.sensor_name,
                                    "model":x.model.sensor_model,
                                    "id":x.pk,
                                    "latest_update": parse_date(sensor_data_dates[str(x.pk)][2]),
                                    "filename": sensor_data_dates[str(x.pk)][0],
                                    "file_type": sensor_data_dates[str(x.pk)][1]},
                                    Sensor.objects.all()))
    context['sensors'] = sensors
    return render(request, 'management/data.html', context)

#list specific sensor data
@login_required
def browse_sensor_data(request, id):
    sensor_object = get_object_or_404(Sensor, pk=id)
    data = get_data_files(sensor_object)
    files = []
    if data != FAILURE:
        data_as_json = data.json()
        data_as_dict = dict(data_as_json)
        for key in data_as_dict:
            files.append({"filename":key, "file_type":data_as_dict[key][0], "date":parse_date(data_as_dict[key][1])})
    context = {}
    context['files'] = files
    context['sensor_id'] = sensor_object.sensor_id
    return render(request, 'management/browse_sensor_data.html', context)

#Display data info
@login_required
def display_sensor_data(request, id, filename):
    sensor_object = get_object_or_404(Sensor, pk=id)
    data = get_datafile(filename, sensor_object)
    date_and_type = get_date_and_type(filename, sensor_object)
    data_previous_and_next = get_previous_and_next(filename, sensor_object)
    if data != FAILURE and date_and_type != FAILURE and data_previous_and_next != FAILURE:
        context = {}
        list_of_data = data.text.splitlines()
        titles = list_of_data[0].split(",") #list of titles
        data_as_dict = {}
        #Creating keys to dictionary
        for i in range(0, len(titles)):
            data_as_dict[titles[i]] = []
        #Adding values to dictionary
        for i in range(1, len(list_of_data)):
            j = 0
            values = [float(value.strip()) for value in list_of_data[i].split(",")]
            for title in titles:
                data_as_dict[title].append(values[j])
                j += 1
        date_and_type = (dict(date_and_type.json()))
        previous_and_next = (dict(data_previous_and_next.json()))
        context['previous'] = previous_and_next['previous']
        context['next'] = previous_and_next['next']
        context['graph_data'] = json.dumps(data_as_dict)
        context['filename'] = filename
        context['file_type'] = date_and_type['type']
        context['sensor_id'] = id
        context['date'] = parse_date(date_and_type['date'])
        return render(request, 'management/display_data.html', context)
    context = {'title':'No data available', 'error_msg':'There is an error with data server'}
    return render(request, 'management/error.html', context)

#Visualize data
@login_required
def visualize_sensor_data(request, id, filename):
    sensor_object = get_object_or_404(Sensor, pk=id)
    data = get_datafile(filename, sensor_object)
    data_previous_and_next = get_previous_and_next(filename, sensor_object)
    if data != FAILURE and data_previous_and_next != FAILURE:
        context = {}
        list_of_data = data.text.splitlines()
        titles = list_of_data[0].split(",") #list of titles
        data_as_dict = {}
        #Creating keys to dictionary
        for i in range(0, len(titles)):
            data_as_dict[titles[i]] = []
        #Adding values to dictionary
        for i in range(1, len(list_of_data)):
            j = 0
            values = [float(value.strip()) for value in list_of_data[i].split(",")]
            for title in titles:
                data_as_dict[title].append(values[j])
                j += 1
        previous_and_next = (dict(data_previous_and_next.json()))
        context['previous'] = previous_and_next['previous']
        context['next'] = previous_and_next['next']
        context['graph_data'] = json.dumps(data_as_dict)
        context['filename'] = filename
        context['sensor_id'] = id
        return render(request, 'management/visualize.html', context)
    context = {'title':'No data available', 'error_msg':'There is an error with data server'}
    return render(request, 'management/error.html', context)

#Table data
@login_required
def table_sensor_data(request, id, filename):
    sensor_object = get_object_or_404(Sensor, pk=id)
    data = get_datafile(filename, sensor_object)
    if data != FAILURE:
        context = {}
        list_of_data = data.text.splitlines()
        titles = list_of_data[0].split(",") #list of titles
        data_as_dict = {}
        #Creating keys to dictionary
        for i in range(0, len(titles)):
            data_as_dict[titles[i]] = []
        #Adding values to dictionary
        for i in range(1, len(list_of_data)):
            j = 0
            values = [float(value.strip()) for value in list_of_data[i].split(",")]
            for title in titles:
                data_as_dict[title].append(values[j])
                j += 1
        context['graph_data'] = json.dumps(data_as_dict)
        context['filename'] = filename
        return render(request, 'management/table_data.html', context)
    context = {'title':'No data available', 'error_msg':'There is an error with data server'}
    return render(request, 'management/error.html', context)

#Download
@login_required
def download_sensor_data(request, id, filename, file_type):
    sensor_object = get_object_or_404(Sensor, pk=id)
    data = get_datafile(filename, sensor_object)
    if data != FAILURE:
        response = HttpResponse(data.text, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename + "." + file_type)
        return response
    context = {'title':'No data available', 'error_msg':'There is an error with data server'}
    return render(request, 'management/error.html', context)

#Delete datafile
@login_required
def delete_datafile(request, id, filename):
    sensor_object = get_object_or_404(Sensor, pk=id)
    delete_datafile_from_data_server(filename, sensor_object)
    return redirect("/data/{}".format(id))

#instructions
@login_required
def instructions_add_sensor(request):
    return render(request, 'management/instructions_add_sensor.html')

@login_required
def instructions_server(request):
    return render(request, 'management/instructions_server.html')

@login_required
def download_instructions(request, file):
    if file == "main":
        with open("management/static/management/instructions/" + "main.py", "r") as f:
            list_of_lines = f.readlines()
            filename = "main.py"
    elif file == "boot":
        with open("management/static/management/instructions/" + "boot.py", "r") as f:
            list_of_lines = f.readlines()
            filename = "boot.py"
    else:
        raise Http404("Page doesn't exist")
    content = "".join(list_of_lines)
    response = HttpResponse(content, content_type='text/x-python')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response

#show user's profile and modify user information
@login_required
def profile(request):
    return render(request, 'management/profile.html')

#signup
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user.is_active = False
            user.save()
            """If user is logged in automatically"""
            #user = authenticate(username=username, password=raw_password)
            #login(request, user)
            return render(request, 'management/success.html', {'title': "Signup completed", 'msg' : "Wait until admin confirms your account."})
    else:
        form = SignUpForm()
    return render(request, 'management/signup.html', {'form': form})
