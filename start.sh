#!/bin/bash
# source /root/vpn_server/venv/bin/activate
/snap/bin/docker-compose -f /root/vpn_server/deployment/docker-compose.yml up -d

/root/vpn_server/venv/bin/python3 /root/vpn_server/crypton/manage.py runserver 0.0.0.0:8000
