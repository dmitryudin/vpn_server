#!/bin/bash
source /root/vpn_server/venv/bin/activate
python3 /root/vpn_server/crypton/manage.py runserver 0.0.0.0:8000
