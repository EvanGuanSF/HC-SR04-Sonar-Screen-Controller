#!/bin/bash

# Set up variables.
INSTALL_DIR=/usr/local/sbin/screen_controller

# Stop services.
sudo systemctl stop screen_controller
sudo systemctl disable screen_controller

# Stop any old running instance of the scripts/programs.
sudo pkill -f ".*Sonar_Screen_Controller.py"

# Clear old files.
sudo rm -rf INSTALL_DIR
sudo systemctl daemon-reload