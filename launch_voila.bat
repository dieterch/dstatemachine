@echo off
cd /d C:\Users\ChvatDi00\projects\dstatemachine
call venv\Scripts\activate.bat
echo c.ServerApp.websocket_ping_interval = 300000 > venv\etc\jupyter\jupyter_server_config.py
echo c.ServerApp.websocket_ping_timeout = 250000 >> venv\etc\jupyter\jupyter_server_config.py
python -m voila App.ipynb
rem python -m jupyterlab App.ipynb
