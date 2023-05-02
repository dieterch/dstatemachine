dStatemachine
========

Python INNIO Myplant Statemchine based Field debugger software. Download data on each engine Start and extract
Data based on Engine states. Find Anomalies and analyse them in depth.

Installation
------------

**Windows:**

Create and activate a virtual environment:
:: 
  git clone https://github.com/dieterch/dstatemachine.git
  cd dstatemachine
  python -m venv venv
  .\venv\Scripts\activate.bat (windows)
  source ./venv/bin/activate (OSX, Linux)
  pip install -r requirements.txt
::

Start
------
>  jupyter lab
     
first run ./Tools/login.ipynb and every following 31 days, you are prompted for your myplant.
login and credentials:
::
  Please enter your myPlant login:
  User: xxxxxxx
  Password: xxxxxxxx
  TOTP Secret: xxxxxxxxx
::

go to the settings tab and update the installed fleet data

Release History
---------------

-  0.1.0
-  Work in progress

Meta
----

Your Name – dieter.chvatal@gmail.com

Distributed under the MIT license. See ``LICENSE`` for more information.

`https://github.com/dieterch/dstatemachine <https://github.com/dieterch/>`__


Contributing
------------

1. Fork it (https://github.com/dieterch/dstatemachine)
2. Create your feature branch (``git checkout -b feature/fooBar``)
3. Commit your changes (``git commit -am 'Add some fooBar'``)
4. Push to the branch (``git push origin feature/fooBar``)
5. Create a new Pull Request

