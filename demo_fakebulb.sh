#!/bin/sh
cp fakebulb.conf ~/.homebridge/config.json 
rm ~/.homebridge/accessories/cachedAccessories
rm ~/.homebridge/persist/*
homebridge
