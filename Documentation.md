# Documentation

Documentation for Sensor Management System

### Python version

Python version should be 3.6 or newer

### Needed libraries

* [Django 2.1](https://www.djangoproject.com/) 
* [ntplib](https://pypi.org/project/ntplib/)
* [Django REST framework](https://www.django-rest-framework.org/)
* [SimpleJWT](https://github.com/davesque/django-rest-framework-simplejwt) 
* [Rest Framework Generic Relations](https://github.com/Ian-Foote/rest-framework-generic-relations)
* [Requests](http://docs.python-requests.org/en/master/)
* [PyCryptodome](https://pycryptodome.readthedocs.io/en/latest/src/introduction.html)

To install libraries run:

```
sudo pip3 install Django==2.1.8 ntplib djangorestframework==3.9.4 rest-framework-generic-relations djangorestframework_simplejwt requests pycryptodome==3.9.0
```

## Getting started

First the database needs to be initialized:
```
python3 manage.py makemigrations management

python3 manage.py migrate
```

Run script add_objects_to_db.py:
```
python3 add_objects_to_db.py
```
Create superuser:
```
python3 manage.py createsuperuser
```

Configure your network to have either a public IP address or place all sensor nodes at the same local network.

Change the ALLOWED_HOSTS in sensor_management_platform/settings.py to match your network settings.

Change the SECRET_KEY in sensor_management_platform/settings.py.

Set DEBUG = False in sensor_management_platform/settings.py.

Run server:
```
python3 manage.py runserver <ip_address>:<port>
```

Go to <ip_address_to_platform>/admin

Select Users and select your superuser

From the bottom change auth level to admin.

## Software update process

Updates are asked periodically by a sensor node. The interval is defined by Update check limit.

When asking an update, sensor nodes sends the following JSON string, which is encyrpted with AES 128-bit CBC.
```
'{
    "sensor_id":"<sensor_id>",
    "sensor_key":"<sensor_key>",
    "software_version":"<software_version>",
    "session_key":"<session_key>"
}'
```
The explanations of parameters:
sensor_id is the unique id of a sensor node. It is given to the node in the creation and can't be changed afterwards. For example: "13"
sensor_key is alphanumeric 20-character string used to verify the identity of the sensor node. Keep this secret. For example: "J422bQm4VBaxTvIIlFm3"
software_version is the current software versio, which sensor node is using. Basically, this is the id of the sensor + timestamp of the creation of software. For example: "10_2019_11_22_11_02_01.txt"
session_key is random 128-bit key used to prevent replay attacks. For example: "8f2da3bdb400c8fc522258f07ead70e6" (as hex).







