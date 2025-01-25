#!/bin/bash
cp ./crypton_vpn.service /lib/systemd/system/
systemctl daemon-reload
systemctl enable crypton_vpn.service
