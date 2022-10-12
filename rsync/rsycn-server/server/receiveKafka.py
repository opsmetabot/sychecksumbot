# pip install kafka-python
from kafka import KafkaConsumer
import json
import etcd3
import hashlib
import os
import yaml


def readEtcdCofig(configName):
  with open(configName) as ya:
    cfg = yaml.safe_load(ya)
    return cfg

def setEtcdValue(dict, etcd):
    for key, value in dict.items():
      etcd.put(key, value)

def connectEtcd(cfg):
  host = cfg['etcd']['host']
  port = cfg['etcd']['port']
  password = cfg['etcd']['password']
  etcd = etcd3.client(host, port)
  return etcd

def receiveData(conf,etcd):

  consumer = KafkaConsumer(bootstrap_servers=conf['host'], group_id=conf['groupid'])

  print('consumer start to consuming...')
  consumer.subscribe((conf['topic'],))
  for message in consumer:
    if message.key!=None:
      key = message.key.decode("utf-8").strip()
      if key == "\"etcd\"":
        msg = json.loads(json.loads(message.value.decode("utf-8")))
        etcdData = {}
        for k,v in msg.items():
          etcdData[k] = v
          print(k,"---",v)
        setEtcdValue(etcdData,etcd)


if __name__ == '__main__':
  cfg = readEtcdCofig("etcdScript.yaml")
  conf = cfg["kafka"]
  etcd = connectEtcd(cfg)
  receiveData(conf,etcd)
