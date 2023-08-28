#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request
import os
import requests 
from datetime import datetime
import json
import paho.mqtt.client as mqtt
import time
import sys

def load_configurations(file_name):
    with open(file_name, 'r') as json_file:
        return json.load(json_file)
json_file = sys.argv[1]
print(json_file)
configurations = load_configurations(json_file)

# Iterate through configuratioSns
for config in configurations:
    client = mqtt.Client()
    broker_ip = config["broker_address"]
    topic = config["topic"]
    topic_2 = config["topic_2"]
    print(broker_ip)
    client.connect(broker_ip)

    while True:
        data_status = {}
        for stream_info in config["streams"]:
            access_token = stream_info["access_token"]
            url = stream_info["url"]
            server_number = stream_info["server_number"]
            live_cu = stream_info["live_cu"]
            print(" working with : ",url)
            try:      
                result = requests.get(url,headers={'Content-Type':'application/json','Authorization': 'Bearer {}'.format(access_token)}, timeout=2)

                data=result.json()
                #print(data)

            except requests.exceptions.RequestException as e:
 
                print("Error: No connection to the server.")       #else:
            json_streams = data.get('streams')
            #client.write_points(json_streams)
            ##print(" [x] Sent %r" % len(json_streams))
            
            json_data =""
            out = {}
            count = 0
            if json_streams is not None:
                for x in range(1, len(json_streams)):
                    json_names = data['streams'][x]['stats']
                    if not (str(json_names.get('status'))) == 'running' :
                        #print( " Name : " + str(data['streams'][x]['name']) + " |    Status : " +  str(json_names.get('status'))  )
                        if not (str(json_names.get('status'))) == 'None' :
                            if not (str(json_names.get('status'))) == 'waiting' :
                                #print( " Name : " + str(data['streams'][x]['name']) + " |    Status : " +  str(json_names.get('status'))  )
                                out[str(data['streams'][x]['name'])] = 1
                                count = count +1 
                            
                            #json_data = json.dumps(data)
                
                data_status[str(len(json_streams))+"_#"+live_cu +"_"+server_number]=count
                payload_str =json.dumps(out)
                print(" [x] Sent %r" % out)
                topic_2="data/tech9/"+live_cu+"/status/error"+"_"+server_number
                print("topic_2",topic_2)
                client.publish(topic_2, payload_str)

                json_status =json.dumps(data_status)


                client.publish(topic, json_status)
                

                time.sleep(1)
            else :
                print("server doesnt have json : ",)
