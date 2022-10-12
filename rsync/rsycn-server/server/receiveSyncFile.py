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

def writeFile(filePath,data):
  print(os.path.split(os.path.realpath(filePath))[0])
  if not os.path.isdir(os.path.split(os.path.realpath(filePath))[0]):
    os.makedirs(os.path.split(os.path.realpath(filePath))[0])
  with open(filePath, 'wb')as file:
      file.write(data)

def rename(filePath):
  if os.path.exists(filePath):
    fileName =  os.path.split(os.path.realpath(filePath))[1]
    fileDir = os.path.split(os.path.realpath(filePath))[0]
    os.rename(filePath,os.path.join(fileDir,".deleted."+fileName))


def connectEtcd(cfg):
  host = cfg['etcd']['host']
  port = cfg['etcd']['port']
  password = cfg['etcd']['password']
  etcd = etcd3.client(host, port)
  return etcd

def receiveData(conf):

  consumer = KafkaConsumer(bootstrap_servers=conf['host'], group_id=conf['groupid'])

  print('consumer start to consuming...')
  consumer.subscribe((conf['topic'],))
  for message in consumer:
    print(message.key)
    if message.key!=None:
      key = json.loads(message.key.decode("utf-8"))
      print(key)
      print(message.value)
      if message.value==b"null":
        rename(key)
      else:
        writeFile(key,message.value)



if __name__ == '__main__':
  cfg = readEtcdCofig("receiveSyncFile.yaml")
  conf = cfg["kafka"]
  receiveData(conf)
