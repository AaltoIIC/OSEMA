from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse, Http404, JsonResponse

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from django.template.response import TemplateResponse

from .models import User, Sensor, Type_of_sensor, Value_pair, Sensitivity, Sample_rate, Sensor, Wlan, Nb_iot, HTTP, HTTPS, Update, MQTT, Data_format, Variable, Default_variable
from .forms import ModifySensorForm, ModifySensorFormLocked, AddSensorForm, SignUpForm, TypeOfSensorInfoLockedForm
from .forms import ModifyWlanForm, ModifyNbIotForm, ModifyHTTPForm, ModifyHTTPSForm, ModifyMQTTForm
from .forms import ModifyDataFormatForm, ModifyVariableForm, ModifyDefaultVariableForm
from .forms import WlanInfoForm, NbIotInfoForm, HTTPInfoForm, HTTPSInfoForm, MQTTInfoForm, VariableInfoForm
from django.forms.formsets import formset_factory
from management.utils import update_sensor, create_new_sensor, parse_date
from .api_permissions import AuthLevel2Permission
from rest_framework.decorators import api_view

from sensor_management_platform.settings import FAILURE, BASE_DIR

from rest_framework import viewsets

import datetime

import os

import string

try:
    import secrets
    def generate_password(length):
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(length))
except:
    def generate_password(length):
        return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))



from .serializers import SensorSerializer, ModelSerializer, NbIotSerializer, WlanSerializer, HTTPSerializer, MQTTSerializer
from .serializers import HTTPSSerializer, SampleRateSerializer, SensitivitySerializer, ValuePairSerializer, DataFormatSerializer, VariableSerializer, DefaultVariableSerializer

import json
from itertools import chain

AVAILABLE_PROTOCOLS_CLASSES = [HTTP, HTTPS, MQTT]
AVAILABLE_PROTOCOLS = ['HTTP', 'HTTPS', 'MQTT']
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

class HTTPViewSet(viewsets.ModelViewSet):
    queryset = HTTP.objects.all()
    serializer_class = HTTPSerializer
    permission_classes = [AuthLevel2Permission]

class HTTPSViewSet(viewsets.ModelViewSet):
    queryset = HTTPS.objects.all()
    serializer_class = HTTPSSerializer
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

class DataFormatViewSet(viewsets.ModelViewSet):
    queryset = Data_format.objects.all()
    serializer_class = DataFormatSerializer
    permission_classes = [AuthLevel2Permission]

class VariableViewSet(viewsets.ModelViewSet):
    queryset = Variable.objects.all()
    serializer_class = VariableSerializer
    permission_classes = [AuthLevel2Permission]

class DefaultVariableViewSet(viewsets.ModelViewSet):
    queryset = Default_variable.objects.all()
    serializer_class = DefaultVariableSerializer
    permission_classes = [AuthLevel2Permission]

@api_view(['POST'])
def get_update(request):
    if request.method == 'POST':
        sensor_object = get_object_or_404(Sensor, pk=request.POST['sensor_id'])
        sensor_object.software_version = request.POST['software_version']
        sensor_object.save()
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
            sensor_object.save()
            return HttpResponse("OK", content_type='text/plain')
        elif sensor_object.sensor_key_old == request.POST['sensor_key']:
            alphabet = string.ascii_letters + string.digits
            sensor_object.sensor_key_old = ''.join(generate_password(20)) #generate random 20-character alphanumeric password
            sensor_object.status = Sensor.MEASURING_UP_TO_DATE
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
    VariableFormSet = formset_factory(ModifyVariableForm, extra=0)
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
                if protocol == 'HTTP':
                    instance = HTTP.objects.get(pk=request.POST['protocol_instance'])
                    modified_http_form = ModifyHTTPForm(request.POST, instance=instance, prefix='http')
                    protocol_instances = HTTP.objects.all()
                    modify_protocol_form = modified_http_form
                    if modified_http_form.is_valid():
                        modified_http_form.save()
                        new_sensor.protocol_object = instance
                    else:
                        errors = True
                elif protocol == 'HTTPS':
                    instance = HTTPS.objects.get(pk=request.POST['protocol_instance'])
                    modified_https_form = ModifyHTTPSForm(request.POST, instance=instance, prefix='https')
                    protocol_instances = HTTPS.objects.all()
                    modify_protocol_form = modified_https_form
                    if modified_https_form.is_valid():
                        modified_https_form.save()
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
                variable_formset = VariableFormSet(request.POST)
                if variable_formset.is_valid():
                    for variable_form in variable_formset:
                        name = variable_form.cleaned_data.get('name')
                        unit = variable_form.cleaned_data.get('unit')
                        if name and unit:
                            v = Variable(sensor=new_sensor, name=name, unit=unit)
                            v.save()
                else:
                    errors = True
                if not errors:
                    new_sensor.status = Sensor.WAITING_FOR_UPDATE
                    new_sensor.adder = user
                    new_sensor.latest_modifier = user
                    new_sensor.save()
                    create_new_sensor(new_sensor)
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
    default_variables = Default_variable.objects.filter(type_of_sensor=initial_sensor_type)
    initial_data = [{'name': dv.name, 'unit': dv.unit}
                    for dv in default_variables]
    modify_variable_forms = VariableFormSet(initial=initial_data)
    if user.auth_level >= 2:
        if not errors_sensor_form:
            add_sensor_form = AddSensorForm(prefix='add_sensor')
        if not errors:
            modify_communication_form = ModifyWlanForm(instance=communication_object, prefix='wlan')
            communication_instances = Wlan.objects.all()
            modify_protocol_form = ModifyHTTPForm(instance=protocol_object, prefix='http')
            protocol_instances = HTTP.objects.all()
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
                'available_protocols': AVAILABLE_PROTOCOLS,
                'modify_variable_forms': modify_variable_forms,
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
    if protocol == 'HTTP':
        protocol_form = HTTPInfoForm(instance=protocol_object, prefix='http')
    elif protocol == 'HTTPS':
        protocol_form = HTTPSInfoForm(instance=protocol_object, prefix='https')
    elif protocol == 'MQTT':
        protocol_form = MQTTInfoForm(instance=protocol_object, prefix='mqtt')
    else:
        raise Http404("Page doesn't exist")
    latest_modifier = sensor.latest_modifier
    data_format = sensor.data_format
    adder = sensor.adder
    VariableFormSet = formset_factory(VariableInfoForm, extra=0)
    variables = Variable.objects.filter(sensor=Sensor.objects.get(pk=sensor_id))
    initial_data = [{'name': v.name, 'unit': v.unit}
                    for v in variables]
    variable_forms = VariableFormSet(initial=initial_data)
    context =   {'sensor_form' : sensor_form,
                'current_sample_rate': sensor.sample_rate.sample_rate,
                'current_sensitivity': sensor.sensitivity.sensitivity,
                'adder' : adder,
                'latest_modifier' : latest_modifier,
                'communication_technology' : communication_type,
                'communication_form' : communication_form,
                'protocol_form': protocol_form,
                'sensor_id': sensor_id,
                'protocol' : protocol,
                'variable_forms': variable_forms,
                'data_format': data_format
    }
    return render(request, 'management/sensor_info.html', context)

@login_required
def return_software_file(request, sensor_id):
    if request.user.auth_level > 1:
        sensor_object = get_object_or_404(Sensor, pk=sensor_id)
        update = Update.objects.filter(sensor=sensor_object).order_by('-date')[0]
        try:
            with open(BASE_DIR + 'management/sensor_updates/' + update.filename, 'r') as f:
                content = f.read()
                response = HttpResponse(content, content_type='text/x-python')
                response['Content-Disposition'] = 'attachment; filename={0}'.format("main.py")
                return response
        except:
            raise Exception("PATH: ", os.getcwd())
    else:
        return render(request, 'management/error.html', {'title' : 'Not authorized', 'error_msg' : 'Ask rights to download sensor from admin.'})

@login_required
def modify_sensor(request, sensor_id):
    errors = False
    user = request.user
    VariableFormSet = formset_factory(ModifyVariableForm, extra=0)
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
            if protocol == 'HTTP':
                instance = HTTP.objects.get(pk=request.POST['protocol_instance'])
                modified_http_form = ModifyHTTPForm(request.POST, instance=instance, prefix='http')
                protocol_instances = HTTP.objects.all()
                modify_protocol_form = modified_http_form
                if modified_http_form.is_valid():
                    modified_http_form.save()
                    modified_sensor.protocol_object = instance
                else:
                    errors = True
            elif protocol == 'HTTPS':
                instance = HTTPS.objects.get(pk=request.POST['protocol_instance'])
                modified_https_form = ModifyHTTPSForm(request.POST, instance=instance, prefix='https')
                protocol_instances = HTTPS.objects.all()
                modify_protocol_form = modified_https_form
                if modified_https_form.is_valid():
                    modified_https_form.save()
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
            variable_formset = VariableFormSet(request.POST)
            if variable_formset.is_valid():
                old_variables = Variable.objects.filter(sensor=modified_sensor)
                for o in old_variables:
                    o.delete()
                for variable_form in variable_formset:
                    name = variable_form.cleaned_data.get('name')
                    unit = variable_form.cleaned_data.get('unit')
                    if name and unit:
                        v = Variable(sensor=modified_sensor, name=name, unit=unit)
                        v.save()
            else:
                errors = True
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
            if protocol == 'HTTP':
                modify_protocol_form = ModifyHTTPForm(instance=protocol_object, prefix='http')
                protocol_instances = HTTP.objects.all()
            elif protocol == 'HTTPS':
                modify_protocol_form = ModifyHTTPSForm(instance=protocol_object, prefix='https')
                protocol_instances = HTTPS.objects.all()
            elif protocol == 'MQTT':
                modify_protocol_form = ModifyMQTTForm(instance=protocol_object, prefix='mqtt')
                protocol_instances = MQTT.objects.all()
            else:
                raise Http404("Page doesn't exist")
    else:
        return render(request, 'management/error.html', {'title' : 'You are not allowed to modify sensor', 'error_msg' : 'Ask rights to modify sensor from admin.'})
    variables = Variable.objects.filter(sensor=Sensor.objects.get(pk=sensor_id))
    initial_data = [{'name': v.name, 'unit': v.unit}
                    for v in variables]
    modify_variable_forms = VariableFormSet(initial=initial_data)
    available_sample_rates = Sample_rate.objects.filter(model=sensor.model.pk)
    available_sensitivities = sensor.sample_rate.supported_sensitivities.all()
    current_model = sensor.model.sensor_model
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
                'available_protocols': AVAILABLE_PROTOCOLS,
                'modify_variable_forms': modify_variable_forms,
                'sensor_id': sensor_id,
                'current_model': current_model,
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

def get_default_variables(request, sensor_model):
    sensor_model_obj = get_object_or_404(Type_of_sensor, pk=sensor_model)
    default_variables = Default_variable.objects.filter(type_of_sensor=sensor_model)
    initial_data = [{'name': dv.name, 'unit': dv.unit}
                    for dv in default_variables]
    VariableFormSet = formset_factory(ModifyVariableForm, extra=0)
    return render(request, 'management/variable_table.html', context = {'modify_variable_forms': VariableFormSet(initial=initial_data)})

def get_sensor_variables(request, sensor_id):
    variables = Variable.objects.filter(sensor=Sensor.objects.get(pk=sensor_id))
    initial_data = [{'name': v.name, 'unit': v.unit}
                    for v in variables]
    VariableFormSet = formset_factory(ModifyVariableForm, extra=0)
    return render(request, 'management/variable_table.html', context = {'modify_variable_forms': VariableFormSet(initial=initial_data)})


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
    if type == "HTTP":
        instances = HTTP.objects.all()
    elif type == "HTTPS":
        instances = HTTPS.objects.all()
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
    if type == 'HTTP':
        protocol_object = get_object_or_404(HTTP, pk=id)
        modify_protocol_form = ModifyHTTPForm(instance=protocol_object, prefix='http')
    elif type == 'HTTPS':
        protocol_object = get_object_or_404(HTTPS, pk=id)
        modify_protocol_form = ModifyHTTPSForm(instance=protocol_object, prefix='https')
    elif type == 'MQTT':
        protocol_object = get_object_or_404(MQTT, pk=id)
        modify_protocol_form = ModifyMQTTForm(instance=protocol_object, prefix='mqtt')
    else:
        raise Http404("Page doesn't exist")
    return JsonResponse(json.dumps(modify_protocol_form.as_table()), safe=False)

@login_required
def get_protocol_form_blank(request, type):
    if type == 'HTTP':
        modify_protocol_form = ModifyHTTPForm(prefix='http')
    elif type == 'HTTPS':
        modify_protocol_form = ModifyHTTPSForm(prefix='https')
    elif type == 'MQTT':
        modify_protocol_form = ModifyMQTTForm(prefix='mqtt')
    else:
        raise Http404("Page doesn't exist")
    return JsonResponse(json.dumps(modify_protocol_form.as_table()), safe=False)

@login_required
def delete_sensor(request, sensor_id):
    user = request.user
    if user.auth_level >= 2:
        sensor_object = Sensor.objects.get(pk=sensor_id)
        sensor_object.delete()
        return redirect('browse_sensors')
    else:
        return render(request, 'management/error.html', {'title' : 'You are not allowed to delete sensor', 'error_msg' : 'Ask rights to delete sensor from admin.'})


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
    if type == 'HTTP':
        communication_object = get_object_or_404(HTTP, pk=id)
        form = HTTPInfoForm(instance=communication_object)
    elif type == 'HTTPS':
        communication_object = get_object_or_404(HTTPS, pk=id)
        form = HTTPSInfoForm(instance=communication_object)
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
                                HTTP.objects.all()))
    https_instances = list(map(lambda x: {"name":x.name, 'type':x.__class__.__name__, "id":x.pk},
                                HTTPS.objects.all()))
    mqtt_instances = list(map(lambda x: {"name":x.name, 'type':x.__class__.__name__, "id":x.pk},
                                MQTT.objects.all()))
    context['http_instances'] = http_instances
    context['https_instances'] = https_instances
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
            if protocol ==  'HTTP':
                modified_form = ModifyHTTPForm(request.POST, prefix='http')
            elif protocol == 'HTTPS':
                modified_form = ModifyHTTPSForm(request.POST, prefix='https')
            elif protocol == 'MQTT':
                modified_form = ModifyMQTTForm(request.POST, prefix='mqtt')
            else:
                raise Http404("Page doesn't exist")
            if modified_form.is_valid():
                modified_form.save()
            return redirect('browse_protocols')
    context =   {'available_protocols': AVAILABLE_PROTOCOLS,
                'protocol_form': ModifyHTTPForm(prefix='http'),
                'initial_protocol': 'HTTP'
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
            if type == 'HTTP':
                protocol_object = get_object_or_404(HTTP, pk=id)
                modify_protocol_form = ModifyHTTPForm(request.POST, instance=protocol_object, prefix='http')
            elif type == 'HTTPS':
                protocol_object = get_object_or_404(HTTPS, pk=id)
                modify_protocol_form = ModifyHTTPSForm(request.POST, instance=protocol_object, prefix='https')
            elif type == 'MQTT':
                protocol_object = get_object_or_404(MQTT, pk=id)
                modify_protocol_form = ModifyMQTTForm(request.POST, instance=protocol_object, prefix='mqtt')
            else:
                raise Http404("Page doesn't exist")
            if modify_protocol_form.is_valid():
                modify_protocol_form.save()
                return redirect('browse_protocols')
    if user.auth_level >= 2:
        if type == 'HTTP':
            protocol_object = get_object_or_404(HTTP, pk=id)
            form = ModifyHTTPForm(instance=protocol_object, prefix='http')
        elif type == 'HTTPS':
            protocol_object = get_object_or_404(HTTPS, pk=id)
            form = ModifyHTTPSForm(instance=protocol_object, prefix='https')
        elif type == 'MQTT':
            protocol_object = get_object_or_404(MQTT, pk=id)
            form = ModifyMQTTForm(instance=protocol_object, prefix='mqtt')
        else:
            raise Http404("Page doesn't exist")
    else:
        if type == 'HTTP':
            protocol_object = get_object_or_404(HTTP, pk=id)
            form = HTTPInfoForm(instance=protocol_object, prefix='http')
        elif type == 'HTTPS':
            protocol_object = get_object_or_404(HTTPS, pk=id)
            form = HTTPSInfoForm(instance=protocol_object, prefix='https')
        elif type == 'MQTT':
            protocol_object = get_object_or_404(MQTT, pk=id)
            form = MQTTInfoForm(instance=protocol_object, prefix='mqtt')
        else:
            raise Http404("Page doesn't exist")
    return render(request, 'management/modify_protocol.html', {'form': form})

@login_required
def delete_protocols(request, type, id):
    if type == 'HTTP':
        HTTP.objects.filter(pk=id).delete()
    elif type == 'HTTPS':
        HTTPS.objects.filter(pk=id).delete()
    elif type == 'MQTT':
        MQTT.objects.filter(pk=id).delete()
    else:
        raise Http404("Page doesn't exist")
    return redirect('browse_protocols')

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
