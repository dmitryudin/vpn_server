#!/bin/bash
apt update
apt install python3-pip
source /root/vpn_server/venv/bin/activate
pip3 install -r /root/vpn_server/requirements.txt
snap install docker
docker-compose up 
cp ./crypton_vpn.service /lib/systemd/system/
systemctl daemon-reload
systemctl enable crypton_vpn.service
