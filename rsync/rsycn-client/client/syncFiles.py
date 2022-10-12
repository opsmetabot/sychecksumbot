from kafka import KafkaProducer, KafkaConsumer
import json
import etcd3
import hashlib
import os
import yaml
import six
import struct
import sys
import time
import asyncio
from threading import Thread

def readEtcdCofig(configName):
  with open(configName) as ya:
    cfg = yaml.safe_load(ya)
    return cfg

def read_bin(file_name):
  with open(file_name, "rb") as f:
    f_content = f.read()
    content = struct.unpack("B" * len(f_content), f_content)
    f.close()
  return content

def readbF(upfile):
  try:
    with open(upfile, "rb") as fp:
      file1 = fp.read()
    return  file1
  except FileNotFoundError:
    return b"null"

def start_producer(host, topic, msg, key):
  producer = KafkaProducer(bootstrap_servers=host,key_serializer=lambda k: json.dumps(k).encode())
  # 同一个key值，会被送至同一个分区
  future = producer.send(topic, value=msg, key=key)
  try:
    future.get(timeout=10)
    # 监控是否发送成功
  except Exception as e:
    print(str(e))



def receiveData(conf):

  time_start = time.time()
  consumer = KafkaConsumer(bootstrap_servers=conf["receive"]['host'], group_id=conf["receive"]['groupid'])

  print('consumer start to consuming...')
  consumer.subscribe((conf["receive"]['topic']))

  sendConfig = conf["send"]

  prefix = sendConfig["prefix"]

  for message in consumer:
    if message.key!=None:
      key = message.key.decode("utf-8").strip()
      if key == "\"syncFile\"":
        msg = json.loads(json.loads(message.value.decode("utf-8")))
        for k,v in msg.items():
          readPath = "/"+k.strip(prefix)
          r = readbF(readPath)
          
          print(k,readPath,r)
          start_producer(sendConfig["host"],sendConfig["topic"],r,k)

if __name__ == '__main__':
    cfg = readEtcdCofig("syncFile.yaml")
    kafka = cfg["kafka"]
    receiveData(kafka)