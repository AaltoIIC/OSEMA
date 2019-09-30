from django.urls import path, include

from . import views

from rest_framework import routers
from management import views
from django.conf.urls.static import static
from django.conf import settings


from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register('sensors', views.SensorViewSet)
router.register('models', views.ModelViewSet)
router.register('wlans', views.WlanViewSet)
router.register('nb-iots', views.NbIotViewSet)
router.register('http', views.HTTPViewSet)
router.register('https', views.HTTPSViewSet)
router.register('mqtt', views.MQTTViewSet)
router.register('dataformats', views.DataFormatViewSet)
router.register('samplerates', views.SampleRateViewSet)
router.register('sensitivitys', views.SensitivityViewSet)
router.register('valuepairs', views.ValuePairViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('sensors', views.sensors, name='sensors'),
    path('sensors/browse', views.browse_sensors, name='browse_sensors'),
    path('sensors/<int:sensor_id>', views.sensor_info, name='sensor_info'),
    path('sensors/download/software/<int:sensor_id>', views.return_software_file, name='return_software_file'),
    path('sensors/modify/<int:sensor_id>', views.modify_sensor, name='modify_sensor'),
    path('sensors/modify/get_sample_rates/<str:sensor_model>', views.get_available_sample_rates, name='get_available_sample_rates'),
    path('sensors/modify/get_available_sensitivities/<int:sample_rate_id>', views.get_available_sensitivities, name='get_available_sensitivities'),
    path('sensors/modify/get_default_variables/<str:sensor_model>', views.get_default_variables, name='get_default_variables'),
    path('sensors/modify/get_sensor_variables/<int:sensor_id>', views.get_sensor_variables, name='get_sensor_variables'),
    path('get_communication_instances/<str:type>', views.get_communication_instances, name='get_communication_instances'),
    path('get_communication_technology_form/<str:type>/<int:id>', views.get_communication_technology_form, name='get_communication_technology_form'),
    path('get_communication_technology_form/<str:type>', views.get_communication_technology_form_blank, name='get_communication_technology_form_blank'),
    path('get_protocol_form/<str:type>', views.get_protocol_form_blank, name='get_protocol_form_blank'),
    path('get_protocol_form/<str:type>/<int:id>', views.get_protocol_form, name='get_protocol_form'),
    path('get_protocol_instances/<str:type>', views.get_protocol_instances, name='get_protocol_instances'),
    path('sensors/delete/<int:sensor_id>', views.delete_sensor, name='delete_sensor'),
    path('sensors/type/<str:model>', views.sensor_type_info, name='sensor_type_info'),
    path('sensors/add', views.add_sensor, name='add_sensor'),
    path('communication_technologies', views.communication_technologies, name='communication_technologies'),
    path('communication_technologies/<str:type>/<int:id>', views.communication_technologies_info, name='communication_technology_info'),
    path('communication_technologies/browse', views.browse_communication_technologies, name='browse_communication_technologies'),
    path('communication_technologies/add', views.add_communication_technologies, name='add_communication_technologies'),
    path('communication_technologies/modify/<str:type>/<int:id>', views.modify_communication_technologies, name='modify_communication_technologies'),
    path('communication_technologies/delete/<str:type>/<int:id>', views.delete_communication_technologies, name='delete_communication_technologies'),
    path('protocols', views.protocols, name='protocols'),
    path('protocols/<str:type>/<int:id>', views.protocol_info, name='protocol_info'),
    path('protocols/browse', views.browse_protocols, name='browse_protocols'),
    path('protocols/add', views.add_protocols, name='add_protocols'),
    path('protocols/modify/<str:type>/<int:id>', views.modify_protocols, name='modify_protocols'),
    path('protocols/delete/<str:type>/<int:id>', views.delete_protocols, name='delete_protocols'),
    path('instructions/add_sensor', views.instructions_add_sensor, name='instructions_add_sensor'),
    path('instructions/server', views.instructions_server, name='instructions_server'),
    path('instructions/download/<str:file>', views.download_instructions, name='download_instructions'),
    path('get_update', views.get_update, name='get_update'),
    path('report_failure', views.failure, name='failure'),
    path('confirm_update', views.confirm_update, name='confirm_update'),
    path('data/log', views.log_data, name='log_data'),
    path('signup', views.signup, name='signup'),
    path('profile', views.profile, name='profile'),
    path('api/v1.0/', include(router.urls)),
    path('api/v1.0/token/', TokenObtainPairView.as_view()),
    path('api/v1.0/token/refresh/', TokenRefreshView.as_view()),
    path('api/v1.0/api-auth/', include('rest_framework.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
