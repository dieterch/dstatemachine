@echo off
cd /d C:\Users\ChvatDi00\projects\dstatemachine
call venv\Scripts\activate.bat
echo c.ServerApp.websocket_ping_interval = 300000 > venv\etc\jupyter\jupyter_server_config.py
echo c.ServerApp.websocket_ping_timeout = 250000 >> venv\etc\jupyter\jupyter_server_config.py
python -c "import re,pathlib; p=pathlib.Path('venv/Lib/site-packages/jupyter_server/base/websocket.py'); p.write_text(re.sub(r'WS_PING_INTERVAL = \d+', 'WS_PING_INTERVAL = 300000', p.read_text()))"
python -m voila App.ipynb
rem python -m jupyterlab App.ipynb
