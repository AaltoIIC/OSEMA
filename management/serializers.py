from management.models import Sensor, Type_of_sensor, Wlan, Nb_iot, Http, Https, Sample_rate, Sensitivity, Value_pair, LWDTP, MQTT
from rest_framework import serializers
from generic_relations.relations import GenericRelatedField
from management.utils import update_sensor, create_new_sensor


class WlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wlan
        fields = ('id', 'url', 'name', 'ssid', 'security', 'key', 'username')

class NbIotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Nb_iot
        fields = ('id', 'url', 'name', 'settings')

class HttpSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Http
        fields = ('id', 'url', 'name', 'settings', 'path')

class HttpsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Https
        fields = ('id', 'url', 'name', 'settings', 'path')

class LWDTPSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LWDTP
        fields = ('id', 'url', 'name', 'access_token', 'refresh_token')

class MQTTSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MQTT
        fields = ('id', 'url', 'name', 'user', 'key', 'topic', 'data_server_url', 'refresh_token', 'port')

class ModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Type_of_sensor
        fields = ('sensor_model', 'url', 'sensor_information', 'address')

class SensorSerializer(serializers.HyperlinkedModelSerializer):
    communication_object = GenericRelatedField({
        Wlan: serializers.HyperlinkedRelatedField(
            queryset = Wlan.objects.all(),
            view_name='wlan-detail',
        ),
        Nb_iot: serializers.HyperlinkedRelatedField(
            queryset = Nb_iot.objects.all(),
            view_name='nb_iot-detail',
        ),
    })
    protocol_object = GenericRelatedField({
            Http: serializers.HyperlinkedRelatedField(
                queryset = Http.objects.all(),
                view_name='http-detail',
            ),
            Https: serializers.HyperlinkedRelatedField(
                queryset = Https.objects.all(),
                view_name='https-detail',
            ),
            LWDTP: serializers.HyperlinkedRelatedField(
                queryset = LWDTP.objects.all(),
                view_name='lwdtp-detail',
            ),
            MQTT: serializers.HyperlinkedRelatedField(
                queryset = MQTT.objects.all(),
                view_name='mqtt-detail',
            ),
        })

    class Meta:
        model = Sensor
        fields = ('sensor_id', 'url', 'sensor_name', 'model', 'status', 'description', 'location', 'sensor_key', 'sample_rate', 'sensitivity', 'data_send_rate', 'burst_length', 'burst_rate', 'connection_close_limit', 'network_close_limit', 'update_check_limit', 'update_check_ip_address', 'data_server_ip_address', 'communication_object', 'protocol_object')

    def create(self, validated_data):
        s = Sensor.objects.create(  sensor_name = validated_data['sensor_name'],
                        model = validated_data['model'],
                        description = validated_data['description'],
                        location = validated_data['location'],
                        sensor_key = validated_data['sensor_key'],
                        status = validated_data['status'],
                        sample_rate = validated_data['sample_rate'],
                        sensitivity = validated_data['sensitivity'],
                        data_send_rate = validated_data['data_send_rate'],
                        burst_length = validated_data['burst_length'],
                        burst_rate = validated_data['burst_rate'],
                        connection_close_limit = validated_data['connection_close_limit'],
                        network_close_limit = validated_data['network_close_limit'],
                        update_check_limit = validated_data['update_check_limit'],
                        update_check_ip_address = validated_data['update_check_limit'],
                        data_server_ip_address = validated_data['data_server_ip_address'],
                        communication_object = validated_data['communication_object'],
                        protocol_object = validated_data['protocol_object']
        )
        create_new_sensor(s)
        return s

    def update(self, instance, validated_data):
        instance.sensor_name = validated_data['sensor_name']
        instance.model = validated_data['model']
        instance.description = validated_data['description']
        instance.location = validated_data['location']
        instance.sensor_key = validated_data['sensor_key']
        instance.status = validated_data['status']
        instance.sample_rate = validated_data['sample_rate']
        instance.sensitivity = validated_data['sensitivity']
        instance.data_send_rate = validated_data['data_send_rate']
        instance.burst_length = validated_data['burst_length']
        instance.burst_rate = validated_data['burst_rate']
        instance.connection_close_limit = validated_data['connection_close_limit']
        instance.network_close_limit = validated_data['network_close_limit']
        instance.update_check_limit = validated_data['update_check_limit']
        instance.update_check_ip_address = validated_data['update_check_limit']
        instance.data_server_ip_address = validated_data['data_server_ip_address']
        instance.communication_object = validated_data['communication_object']
        instance.protocol_object = validated_data['protocol_object']
        intance.save()
        update_sensor(instance)
        return instance

class SampleRateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sample_rate
        fields = ('id', 'url', 'model', 'supported_sensitivities', 'sample_rate', 'read_values', 'write_values', 'format_string')

class SensitivitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sensitivity
        fields = ('id', 'url', 'model', 'sensitivity', 'read_values', 'write_values', 'format_string')

class ValuePairSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Value_pair
        fields = ('id', 'url', 'value1', 'value2')
