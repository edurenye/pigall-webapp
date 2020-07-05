#!/bin/bash -e

# Start server.
echo "Starting web server..."
export FLASK_APP=/home/pi/webapp/app.py

source /opt/intel/openvino/bin/setupvars.sh

flask run --host=0.0.0.0 --port=80
#flask run --cert=/home/pi/webapp/cert/cert.pem --key=/home/pi/webapp/cert/key.pem --host=0.0.0.0 --port=443
