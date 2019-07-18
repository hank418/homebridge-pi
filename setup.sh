#!/bin/sh

# basic setting
sudo update-rc.d ssh enable
sudo apt-get update 
sudo apt-get install -y vim
sudo rm /etc/localtime
sudo cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime
sudo cp dhcpcd.conf /etc/dhcpcd.conf

# install nodejs 8
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs

