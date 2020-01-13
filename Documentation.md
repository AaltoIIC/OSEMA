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

You can test locally by running (you can change from sensor_managent_platform/settings.py DEBUG=True to serve static files):
```
python3 manage.py runserver
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

Updates are asked periodically by a sensor node using check_update(url, port) function. The interval is defined by Update check limit. Messages can be sent over HTTP or HTTPS. Because of the limited support for certificate checking, HTTPS does not provide sufficient level of security.
Therefore, all messages are encrypted using AES 128-bit CBC and HMAC is calculated (with SHA-256) to ensure authenticity and integrity of the message. This encryption method is itself secure, so messages can be sent also using HTTP. The format of HTTP message body is <message_encrypted>.<hmac_of_the_message>


When asking an update, sensor nodes sends the following JSON string.
```
'{
    "software_version":"<software_version>",
    "session_key":"<session_key>"
}'
```
Explanation of parameters:
* sensor_id is the unique id of a sensor node. It is given to the node in the creation and can't be changed afterwards. For example: "13"
* sensor_key is alphanumeric 20-character string used to verify the identity of the sensor node. Keep this secret. For example: "J422bQm4VBaxTvIIlFm3"
* software_version is the current software versio, which sensor node is using. Basically, this is the id of the sensor + timestamp of the creation of software. For example: "10_2019_11_22_11_02_01.txt"
* session_key is random 128-bit key used to prevent replay attacks. A fresh session key generated each time updates are asked. For example: "8f2da3bdb400c8fc522258f07ead70e6" (as hex).

Server then compares the received software version to the one in the database. If the software versions match, node's software is up-to-date. Server then sets node's status as "Measuring" and responds to request as follows:
```
<session_key>|UP-TO-DATE"
```

If the software version received does not match to the one in the server database, server responds as follows:
```
<session_key>|<software>"
```
Explanation of parameters:
* server_identifier is 128-bit identifier of the server. Keep this secret. Can only be accessed from the admin page. For example: "8f2da3bdb400c8fc522258f07ead70e6" (as hex).
* session_key is used to verify that the server is responding to the recently sent update. For example: "8f2da3bdb400c8fc522258f07ead70e6" (as hex).
* software_hash is Sha-256 hash calculated from the software, which is used to verify that software has not been modified. For example: "82d9b82c978e0b484c91ac30e989ed123124b0813637629ebb0f503579c74c02" (as hex).
* session_key is random 128-bit key used to prevent replay attacks. For example: "8f2da3bdb400c8fc522258f07ead70e6" (as hex).

If the software is up-to-date, a sensor node returns from the function. Otherwise, the node writes new software to its memory and reboots.
In the boot-up the saved file is renamed to main.py. Immediately after boot, the sensor node call check_update function.

## Encryption of data
The measurment data can be enrypted with AES 128-bit CBC.

Currently, this is only implmented for JSON data format.

## Adding new sensor model
* Do not use spaces in the name of the sensor model. Otherwise, it won't work with API.
* The name can't ba changed afterwards, because it is used as a primary key in the database.
