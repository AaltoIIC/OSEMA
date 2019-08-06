# Sensor Configurator Platform

This is interface for controlling PyCom microcontroller boards

### Python version

Python version should be 3.6 or newer

### Needed libraries

* [Django 2.1](https://www.djangoproject.com/) 
* [ntplib](https://pypi.org/project/ntplib/)
* [Django REST framework](https://www.django-rest-framework.org/)
* [SimpleJWT](https://github.com/davesque/django-rest-framework-simplejwt) 
* [Rest Framework Generic Relations](https://github.com/Ian-Foote/rest-framework-generic-relations)
* [Requests](http://docs.python-requests.org/en/master/)

To install libraries run:

```
sudo pip3 install Django==2.1.8 ntplib djangorestframework==3.9.4 rest-framework-generic-relations djangorestframework_simplejwt requests
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

## Authors

* Riku Ala-Laurinaho