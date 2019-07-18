
import paho.mqtt.publish as publish
import json

publish.single("homebridge/to/get", '{"name": "*"}', hostname="127.0.0.1")