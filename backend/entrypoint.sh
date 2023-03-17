#!/bin/sh
set -e
echo "Container's IP address: `awk 'END{print $1}' /etc/hosts`"
cd /backend
ls /vdf
ls /backend/out/
cp -r /vdf /backend/out/