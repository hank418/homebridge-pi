#!/bin/sh
cp mqtt.conf ~/.homebridge/config.json 
rm ~/.homebridge/accessories/cachedAccessories
rm ~/.homebridge/persist/*
homebridge
