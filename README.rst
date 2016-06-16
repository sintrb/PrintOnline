PrintOnline
===============
A online printer manager for Windows.

Install
===============
::

 pip install PrintOnline


Use
===============
cd to you working directory and run command:

::

 PrintOnline.bat

if can't find PrintOnline command, try:
::

 python -m PrintOnline


open broswer with url **http://127.0.0.1:8000**, upload file and print it.


Other tips
===============
1.set http port 80
::

 PrintOnline 80

2.authenticate with username and password (admin admin)
::

 PrintOnline -u admin -p admin

3.set the working directory (/tmp)
::

 PrintOnline -d /tmp

4.bind address with 127.0.0.1
::

 PrintOnline 127.0.0.1:8000
 
5.use as wsgi
::

 # set username and passwor
 export WSGI_PARAMS="-u admin -p admin" 
 # run wsgi with gunicorn
 gunicorn -b 0.0.0.0:8000 PrintOnline.wsgi:application

 