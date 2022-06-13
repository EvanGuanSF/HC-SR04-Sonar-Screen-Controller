#!/bin/bash

# Set up variables.
CUR_DIR=$(pwd)
INSTALL_DIR=/usr/local/sbin/screen_controller

# Create a directory to hold files.
sudo mkdir -p "$INSTALL_DIR"
sudo chmod 744 "$INSTALL_DIR"

# Copy the files to the sbin folder.
sudo cp -f "$CUR_DIR"/Sonar_Screen_Controller.py "$INSTALL_DIR"
sudo cp -f "$CUR_DIR"/Ranger.py "$INSTALL_DIR"

# Copy the service to the main systemd directory.
sudo rm -f /etc/systemd/system/screen_controller.service
sudo cp -f "$CUR_DIR"/screen_controller.service /etc/systemd/system

# Stop any old running instance of the service and restart it.
sudo systemctl daemon-reload
sudo systemctl enable screen_controller
sudo systemctl restart screen_controller