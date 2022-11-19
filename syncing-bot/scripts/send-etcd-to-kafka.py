import getopt
import json
import sys
import etcd3
import yaml
from kafka import KafkaProducer
from loguru import logger
from pykafka import KafkaClient
import os


@logger.catch
def readEtcdCofig(configName):
    with open(configName) as ya:
        cfg = yaml.safe_load(ya)
        return cfg


@logger.catch
def realFile(filePath):
    file_object1 = open(filePath, 'r', encoding="utf-8")
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

@logger.catch
def dirFilesPath(path):

    filePaths = []  # 存储目录下的所有文件名，含路径
    for root, dirs, files in os.walk(path):
        for file in files:
            filePaths.append(os.path.abspath(file))
    return filePaths


@logger.catch
def connectEtcd(cfg):
    host = cfg['etcd']['host']
    port = cfg['etcd']['port']
    password = cfg['etcd']['password']
    etcd = etcd3.client(host, port)
    return etcd


@logger.catch
def getEtcdData(fileList, etcd):
    etcdData = {}
    for filekey in fileList:
        key = filekey.strip()
        record = etcd.get(key)
        print(record)
        if record[0] != None:
            etcdData[key] = record[0].decode('utf-8')
        else:
            etcdData[key] = "null"
    return etcdData


@logger.catch
def sendKafkaMessage(message, cfg):
    KAFKA_HOST = cfg["kafka"]['host']  # Or the address you want
    client = KafkaClient(hosts=KAFKA_HOST)
    topic = client.topics[cfg["kafka"]["topic"]]
    with topic.get_sync_producer() as producer:
        encoded_message = message.encode("utf-8")
        producer.produce(encoded_message)


@logger.catch
def start_producer(host, topic, msg, key):
    producer = KafkaProducer(bootstrap_servers=host, key_serializer=lambda k: json.dumps(k).encode(),
                             value_serializer=lambda v: json.dumps(v).encode(), api_version=((0, 10, 1)))
    # 同一个key值，会被送至同一个分区
    future = producer.send(topic, msg, key=key)

    logger.info("sendMessage:" + msg)

    try:
        future.get(timeout=10)
        # 监控是否发送成功
    except Exception as e:
        print(str(e))


if __name__ == '__main__':

    logger.add('../logs/send-etcd-to-kafka_{time:YYYY-MM-DD}.log',

               level='DEBUG',

               format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',

               rotation="00:00", retention="30 days")

    argv = sys.argv
    try:
        options, args = getopt.getopt(sys.argv[1:], "hf:d:p:", ["help", "fileList=", "dir=","prefix="])
    except getopt.GetoptError:
        sys.exit()

    if len(argv) < 5:
        logger.info("参数错误" + argv)
        print("python3 send-etcd-to-kafka.py [<-f> fileList | <-d> dir] <--prefix> prefix")
        sys.exit()

    if("-f" in argv and "-d" in argv ):
        logger.info("参数错误" + argv)
        print("python3 send-etcd-to-kafka.py [<-f> fileList | <-d> dir] <--prefix> prefix")
        sys.exit()

    if ("-f" not in argv or "--prefix" not in argv) or ("-d" not in argv or "--prefix" not in argv):
        logger.info("参数错误" + argv)
        print("python3 send-etcd-to-kafka.py [<-f> fileList | <-d> dir] <--prefix> prefix")
        sys.exit()

    fileListPath = ""

    # 修改命令行读取
    prefix = ""
    dir = ""

    for name, value in options:
        if name in ("-f", "--fileList"):
            fileListPath = value
        if name in ("-p", "--prefix"):
            prefix = value
        if name in ("-d","--dir"):
            dir = value

    logger.info("fileList:" + fileListPath + "---" + "prefix:" + prefix)

    cfg = readEtcdCofig("syncing.yaml")
    host = cfg["kafka"]["host"]
    topic = cfg["kafka"]["topic"]
    etcd = connectEtcd(cfg)

    fileList = None

    if "-f" in argv:
        fileList = realFile(fileListPath)
    else:
        fileList = dirFilesPath(dir)

    etcdData = getEtcdData(fileList, etcd)

    addPrefix = {}
    for k, v in etcdData.items():
        addPrefix[prefix + k] = etcdData[k]
    print(addPrefix)
    start_producer(host, topic, json.dumps(addPrefix), "etcd")
