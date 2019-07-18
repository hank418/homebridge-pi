import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json


HB_FROM_TOPIC='homebridge/from/#'
HB_FROM_SET_TOPIC='homebridge/from/set'
HB_SET_TOPIC='homebridge/to/set'
HB_GET_TOPIC='homebridge/to/get'
HB_ADD_TOPIC='homebridge/to/add'
HB_ADD_SERVICE_TOPIC='homebridge/to/add/service'

HB_FROM_RESPONSE='homebridge/from/response'

AC_INIT_TOPIC='accessory/init/#'
AC_SET_TOPIC='accessory/set/#'
AC_STATUS_TOPIC='accessory/status/'

#have db save reg IoT Device info

switch_dict = {}

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata,flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(HB_FROM_TOPIC)
    client.subscribe(AC_SET_TOPIC)
    client.subscribe(AC_INIT_TOPIC)
    client.publish(HB_GET_TOPIC, "{\"name\":\"*\"}")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def on_message_hb_from_set(client, userdata, msg):
    # will receive like "{"name": "flex_lamp", "service_name": "light", "characteristic": "On", "value": true}"
    global switch_dict
    obj=json.loads(msg.payload.decode())
    dev_name = obj["name"]
    service = obj["service_name"]
    on = obj['value']
    # print("set from hb " + str(obj))

    switch_dict[dev_name][service] = on
    if dev_name in switch_dict and service in switch_dict[dev_name]:
        tmp_payload = {}
        for key, val in switch_dict[dev_name].items():
            tmp_payload[key] = int(val)
        client.publish(AC_STATUS_TOPIC+dev_name, json.dumps(tmp_payload))
        print("all: " + str(switch_dict))


def on_message_ac_set(client, userdata, msg):
    # will receive like "{"switch1":1,"switch2":0}"
    global switch_dict
    # print("@@ From AC SET"+msg.topic+" "+str(msg.payload))
    dev_name = msg.topic.split("accessory/set/")[1]
    obj=json.loads(msg.payload.decode())

    if dev_name in switch_dict:
        for service, on in obj.items():
            if service in switch_dict[dev_name]:
                switch_dict[dev_name][service] = bool(on)
                client.publish(HB_SET_TOPIC,str("{\"name\": \"%s\", \"service_name\": \"%s\", \"characteristic\": \"On\", \"value\": %s}" % (dev_name, service, str(bool(on)).lower())))
        print("all: " + str(switch_dict))

def on_message_ac_init(client, userdata, msg):
    # will receive like "{"switch1":1,"switch2":0}"
    global switch_dict
    # print("@@ From AC SET"+msg.topic+" "+str(msg.payload))
    dev_name = msg.topic.split("accessory/init/")[1]
    obj=json.loads(msg.payload.decode())
    print("name: " + dev_name + "obj: " + str(obj))
    if dev_name in switch_dict:
        check_service(dev_name, obj)
    else:
        # register
        service = list(obj.keys())[0]
        on = int(list(obj.values())[0])
        tmp_service = {service: bool(on)}
        switch_dict[dev_name] = tmp_service
        client.publish(HB_ADD_TOPIC,str("{\"name\": \"%s\", \"service_name\": \"%s\", \"service\": \"Switch\"}" % (dev_name, service)))
        check_service(dev_name, obj)

    # init status
    for service, on in obj.items():
        client.publish(HB_SET_TOPIC,str("{\"name\": \"%s\", \"service_name\": \"%s\", \"characteristic\": \"On\", \"value\": %s}" % (dev_name, service, str(bool(on)).lower())))
        pass
    print("all: " + str(switch_dict))

def on_message_hb_resp(client, userdata, msg):
    # print("@@ From HB Resp "+msg.topic+" "+str(msg.payload))
    global switch_dict
    obj=json.loads(msg.payload.decode())
    if "ack" in obj:
        pass
    else:
        switch_dict = get_switches_from_hb(obj)
        print("all: " + str(switch_dict))
                    

def get_switches_from_hb(obj):
    # will return like "{'AM001_123456_SW': {'switch2': False, 'switch1': False}}"
    switches = {}
    for name, content in obj.items():
        switch = {}
        for service_name, service_type in content["services"].items():
            value = content["characteristics"][service_name]["On"]
            switch[service_name] = value
        switches[name] = switch
    return switches

def check_service(dev_name, obj):
    # will receive like "{"switch1":1,"switch2":0}"
    for service, on in obj.items():
        if service not in switch_dict[dev_name]:
            #add service 
            switch_dict[dev_name][service] = bool(on)
            client.publish(HB_ADD_SERVICE_TOPIC,str("{\"name\": \"%s\", \"service_name\": \"%s\", \"service\": \"Switch\"}" % (dev_name, service)))
    

client = mqtt.Client()
client.message_callback_add(HB_FROM_SET_TOPIC,on_message_hb_from_set)
client.message_callback_add(AC_SET_TOPIC,on_message_ac_set)
client.message_callback_add(AC_INIT_TOPIC,on_message_ac_init)
client.message_callback_add(HB_FROM_RESPONSE,on_message_hb_resp)


client.on_connect = on_connect
client.on_message = on_message


client.connect("127.0.0.1", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()