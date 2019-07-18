import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json


def on_connect(client, userdata,flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("#")
    client.publish("homebridge/to/get", '{"name": "*"}')
    
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    client.loop_stop() #start the loop


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message


client.connect("127.0.0.1", 1883, 60)
client.loop_forever()
#client.loop_start() #start the loop
#client.publish("homebridge/to/get", '{"name": "*"}')
