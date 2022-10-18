# pip install kafka-python
from kafka import KafkaConsumer, KafkaProducer
import json
import etcd3
import hashlib
import os
import yaml
from loguru import logger

@logger.catch
def readEtcdCofig(configName):
    with open(configName) as ya:
        cfg = yaml.safe_load(ya)
        return cfg

@logger.catch
def setEtcdValue(dict, etcd):
    for key, value in dict.items():
        etcd.put(key, value)

@logger.catch
def connectEtcd(cfg):
    host = cfg['etcd']['host']
    port = cfg['etcd']['port']
    password = cfg['etcd']['password']
    etcd = etcd3.client(host, port)
    return etcd

@logger.catch
def writeFile(filePath, data):
    if not os.path.isdir(os.path.split(os.path.realpath(filePath))[0]):
        print("创建文件夹", filePath)
        os.makedirs(os.path.split(os.path.realpath(filePath))[0])
    with open(filePath, 'wb')as file:
        file.write(data)

@logger.catch
def rename(filePath):
    if os.path.exists(filePath):
        fileName = os.path.split(os.path.realpath(filePath))[1]
        fileDir = os.path.split(os.path.realpath(filePath))[0]
        os.rename(filePath, os.path.join(fileDir, ".deleted." + fileName))

@logger.catch
def start_producer(host, topic, msg, key):
    producer = KafkaProducer(bootstrap_servers=host, key_serializer=lambda k: json.dumps(k).encode(),
                             value_serializer=lambda v: json.dumps(v).encode(), api_version=(0, 1, 0))
    # 同一个key值，会被送至同一个分区
    future = producer.send(topic, msg, key=key)
    try:
        future.get(timeout=10)
        # 监控是否发送成功
    except Exception as e:
        print(str(e))


# 获取文件md5值
@logger.catch
def getFileMd5Value(filePath):
    fileDict = {}
    try:
        md5_value = hashlib.md5(open(filePath, 'rb').read()).hexdigest()
        fileDict[filePath] = md5_value
    except FileNotFoundError:
        fileDict[filePath] = "null"
    return fileDict

@logger.catch
def getEtcdPrefic(etcd, prefic):
    records = etcd.get_prefix(prefic)
    oldEtcdData = {}
    for record in records:
        key = record[1].key.decode('utf-8')
        value = record[0].decode('utf-8')
        oldEtcdData[key] = value
    return oldEtcdData


# 比较etcd checksum
@logger.catch
def compareEtcdData(etcdData):
    defferentDict = {}
    for k, v in etcdData.items():
        newEtcdData = getFileMd5Value(k)
        if v == newEtcdData[k]:
            print("path:", k, "---", "etcdChecksum", v, "---", "fileChecksum:", newEtcdData, "---", "true")
        else:
            print("path:", k, "---", "etcdChecksum", v, "---", "fileChecksum:", newEtcdData, "---", "false")
            defferentDict[k] = v
    return defferentDict

@logger.catch
def receiveData(conf, etcd):
    consumer = KafkaConsumer(bootstrap_servers=conf['host'], group_id=conf['groupid'])

    print('consumer start to consuming...')
    consumer.subscribe((conf["message"]['topic'], conf["file"]['topic']))

    prefix = ""
    if "prefix" in conf:
        prefix = conf["prefix"]

    for message in consumer:
        # 接收kafka消息
        if message.topic == conf["message"]['topic']:
            if message.key != None:
                key = message.key.decode("utf-8").strip()
                if key == "\"etcd\"":
                    msg = json.loads(json.loads(message.value.decode("utf-8")))
                    etcdData = {}
                    for k, v in msg.items():
                        # 添加前缀
                        etcdData[prefix + k] = v
                    setEtcdValue(etcdData, etcd)

                    compareData = getEtcdPrefic(etcd, "/")
                    defferentDict = compareEtcdData(compareData)
                    # 如果有不同的就发过去
                    if (defferentDict != None):
                        sendDefferent = {}
                        # 去除同步文件前缀
                        for k, v in defferentDict.items():
                            sendKey = k[len(prefix):]
                            logger.info("不同文件:"+sendKey+"checkSum:"+v)
                            sendDefferent[sendKey] = defferentDict[k]
                        start_producer(conf['host'], "sync-file", json.dumps(sendDefferent), "syncFile")
        # 同步文件
        if message.topic == conf["file"]['topic']:
            if message.key != None:
                key = json.loads(message.key.decode("utf-8"))
                # 添加前缀
                key = prefix + key
                if message.value == b"null":
                    logger.info("修改文件名"+ key)
                    rename(key)
                else:
                    logger.info("同步文件:"+key)
                    print("write", key)
                    writeFile(key, message.value)


if __name__ == '__main__':
    logger.add('logs/log_{time:YYYY-MM-DD}.log',

               level='DEBUG',

               format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',

               rotation="00:00", retention="30 days")

    logger.info('synced-bot 开始运行')

    cfg = readEtcdCofig("synced-bot.yaml")
    conf = cfg["kafka"]

    etcd = connectEtcd(cfg)
    receiveData(conf, etcd)
