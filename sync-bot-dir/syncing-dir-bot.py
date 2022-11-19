import os
from kafka import KafkaConsumer, KafkaProducer
import json
import etcd3
import hashlib
import os
import yaml
from loguru import logger


@logger.catch
def readYamlConfig(configName):
    with open(configName) as ya:
        cfg = yaml.safe_load(ya)
        return cfg

# 读取目录列表文件
def dirFilesPath(path):
    filePaths = []  # 存储目录下的所有文件名，含路径
    for root, dirs, files in os.walk(path):
        for file in files:
            filePaths.append(os.path.abspath(file))
    return filePaths








@logger.catch
def start_producer(host, topic, msg, key):
    producer = KafkaProducer(bootstrap_servers=host, value_serializer =lambda k: json.dumps(k).encode(),key_serializer=lambda k: json.dumps(k).encode())
    # 同一个key值，会被送至同一个分区
    future = producer.send(topic, value=msg, key=key)
    try:
        future.get(timeout=10)
        # 监控是否发送成功
    except Exception as e:
        print(str(e))

@logger.catch
def writeFile(filePath, data):
    if not os.path.isdir(os.path.split(os.path.realpath(filePath))[0]):
        print("创建文件夹", filePath)
        os.makedirs(os.path.split(os.path.realpath(filePath))[0])
    with open(filePath, 'wb')as file:
        file.write(data)





@logger.catch
def receiveData(conf):
    consumer = KafkaConsumer(bootstrap_servers=conf["kafka"]['host'], group_id=conf["kafka"]['groupid'])

    print('consumer start to consuming...')
    consumer.subscribe((conf["kafka"]["checksum"]['topic'],conf["kafka"]["file"]['topic']))

    sendConfig = conf["kafka"]["deference"]

    for message in consumer:

        # 接收kafka消息
        if message.topic == conf["kafka"]["checksum"]['topic']:
            msg = json.loads(str(message.value,encoding="utf-8"))
            if msg.get("targetDir") is not None and msg.get("absDirPath") is not None and msg.get("data") is not None:
                if not os.path.exists(msg["targetDir"]):
                    start_producer(conf["kafka"]["host"],conf["kafka"]["deference"]["topic"],msg,"checksum")
                else:
                    sendData = {}
                    deferenData = {}
                    for k,v in msg["data"].items ():
                        path = msg["targetDir"]+k
                        if not os.path.exists(path):
                            deferenData[k] = "null"
                        else:
                            md5_value = hashlib.md5(open(path, 'rb').read()).hexdigest()
                            if md5_value!=v:
                                deferenData[k] = md5_value

                    sendData["data"] = json.loads(json.dumps(deferenData))
                    sendData["targetDir"] = msg["targetDir"]
                    sendData["absDirPath"] = msg["absDirPath"]
                    start_producer(conf["kafka"]["host"], conf["kafka"]["deference"]["topic"], sendData, "checksum")
            print(msg)
                # key = message.key.decode("utf-8").strip()
                # if key == "\"checksum\"":
                #     print(message.value)


        # 同步文件
        if message.topic == conf["kafka"]["file"]['topic']:
            print(message.value)
            if message.key != None:
                message.value
                key = json.loads(message.key.decode("utf-8"))
                # 添加前缀
                if message.value == b"null":
                    logger.info("修改文件名" + key)
                else:
                    logger.info("同步文件:" + key)
                    print("write", key)
                    writeFile(key, message.value)



if __name__ == '__main__':
    yamlConfig = readYamlConfig("syncing.yaml")
    receiveData(yamlConfig)