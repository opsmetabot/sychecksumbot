from pykafka import KafkaClient
import threading
import etcd3
import json
import yaml
from kafka import KafkaProducer, KafkaConsumer


def readEtcdCofig(configName):
    with open(configName) as ya:
        cfg = yaml.safe_load(ya)
        return cfg

def realFile(filePath):
    file_object1 = open(filePath, 'r',encoding="utf-8")
    data = []
    try:
        while True:
            line = file_object1.readline()
            if line:
                data.append(line)
            else:
                break
    finally:
        file_object1.close()
    return data

def connectEtcd(cfg):
    host = cfg['etcd']['host']
    port = cfg['etcd']['port']
    password = cfg['etcd']['password']
    etcd = etcd3.client(host,port)
    return etcd


def getEtcdData(fileList,etcd):
    etcdData  = {}
    for filekey in fileList:
        key = filekey.strip()
        record =  etcd.get(key)
        print(record)
        if record[0]!=None:
            etcdData[key] = record[0].decode('utf-8')
        else:
            etcdData[key] = "null"
    return etcdData


def sendKafkaMessage(message,cfg):
    KAFKA_HOST = cfg["kafka"]['host']  # Or the address you want
    client = KafkaClient(hosts=KAFKA_HOST)
    topic = client.topics[cfg["kafka"]["topic"]]
    with topic.get_sync_producer() as producer:
        encoded_message = message.encode("utf-8")
        producer.produce(encoded_message)

def start_producer(host,topic,msg,key):
    producer = KafkaProducer(bootstrap_servers=host, key_serializer=lambda k: json.dumps(k).encode(), value_serializer=lambda v: json.dumps(v).encode(), api_version=((0, 10, 1)))
    # 同一个key值，会被送至同一个分区
    future = producer.send(topic, msg, key=key)
    try:
        future.get(timeout=10)
        # 监控是否发送成功
    except Exception as e:
        print(str(e))

if __name__ == '__main__':
    cfg = readEtcdCofig("etcdScript.yaml")
    host = cfg["kafka"]["host"]
    etcd = connectEtcd(cfg)
    fileListPath = cfg["fileList"]["path"]
    prefix = cfg["kafka"]["prefix"]
    fileList = realFile(fileListPath)
    etcdData = getEtcdData(fileList,etcd)

    addPrefix = {}
    for k,v in etcdData.items():
        addPrefix[prefix+k] = etcdData[k]
    print(addPrefix)
    # sendKafkaMessage(json.dumps(etcdData),cfg)
    start_producer(host,"kafka-test",json.dumps(addPrefix),"etcd")
