import yaml
import hashlib
import etcd3
import json
from kafka import KafkaProducer

def readEtcdCofig(configName):
    with open(configName) as ya:
        cfg = yaml.safe_load(ya)
        return cfg

def connectEtcd(cfg):
    host = cfg['etcd']['host']
    port = cfg['etcd']['port']
    password = cfg['etcd']['password']
    etcd = etcd3.client(host,port)
    return etcd

def getFileMd5Value(filePath):
    fileDict = {}
    try:
        md5_value = hashlib.md5(open(filePath, 'rb').read()).hexdigest()
        fileDict[filePath] = md5_value
    except FileNotFoundError:
        fileDict[filePath] = "null"
    return fileDict

def start_producer(host,topic,msg,key):
    producer = KafkaProducer(bootstrap_servers=host, key_serializer=lambda k: json.dumps(k).encode(), value_serializer=lambda v: json.dumps(v).encode(), api_version=(0, 1, 0))
    # 同一个key值，会被送至同一个分区
    future = producer.send(topic, msg, key=key)
    try:
        future.get(timeout=10)
        # 监控是否发送成功
    except Exception as e:
        print(str(e))

def getEtcdPrefic(etcd,prefic):
    records =  etcd.get_prefix(prefic)
    oldEtcdData = {}
    for record in records:
        key = record[1].key.decode('utf-8')
        value = record[0].decode('utf-8')
        oldEtcdData[key] = value
    return oldEtcdData

def compareEtcdData(etcdData):
    defferentDict = {}
    for k,v in etcdData.items():
        newEtcdData =  getFileMd5Value(k)
        print(k,v)
        print(newEtcdData)
        if v == newEtcdData[k]:
            pass
        else:
            defferentDict[k] = v
    return defferentDict


if __name__ == '__main__':
    cfg = readEtcdCofig("etcdScript.yaml")
    etcd = connectEtcd(cfg)
    etcdData = getEtcdPrefic(etcd,"/")
    defferentDict = compareEtcdData(etcdData)

    syncFileCfg = readEtcdCofig("syncFile.yaml")
    host = syncFileCfg["kafka"]["receive"]["host"]

    if(defferentDict!=None):
        print("defferen",defferentDict)
        start_producer(host,"sync-file",json.dumps(defferentDict),"syncFile")
