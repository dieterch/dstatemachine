@echo off
cd /d C:\Users\ChvatDi00\projects\dstatemachine
call venv\Scripts\activate.bat
python -m voila App.ipynb --websocket_ping_interval=300000 --websocket_ping_timeout=250000
rem python -m jupyterlab App.ipynb
