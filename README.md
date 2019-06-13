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
pip install django ntplib djangorestframework rest-framework-generic-relations djangorestframework_simplejwt requests
```

## Getting started

First the database needs to be initialized:
```
python manage.py makemigrations management

python manage.py migrate
```

Run script add_objects_to_db.py:
```
python add_objects_to_db.py
```
Create superuser:
```
python manage.py create superuser
```

Configure your network so that you have public IP addres.

Run server:
```
python manage.py <ip_address>:<port>
```


## Authors

* Riku Ala-Laurinaho