import hashlib
import json
import os
import sys
import yaml
from kafka import KafkaConsumer, KafkaProducer
from loguru import logger


@logger.catch
def readYamlConfig(configName):
    with open(configName) as ya:
        yamlConfig = yaml.safe_load(ya)
        return yamlConfig

# 读取目录列表文件
def dirFilesPath(path):
    filePaths = []  # 存储目录下的所有文件名，含路径
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filePaths.append(os.path.abspath(os.path.join(dirpath, filename)))
    return filePaths

@logger.catch
def readbin(upfile):
    try:
        with open(upfile, "rb") as fp:
            file1 = fp.read()
        return file1
    except FileNotFoundError:
        return b"null"


# 获取文件md5 值
@logger.catch
def getFileMd5(files,absPath,targetPath):
    # test的文件路径
    dict = {}
    for file in files:
        md5_value = hashlib.md5(open(file, 'rb').read()).hexdigest()
        dict[file.replace(absPath,targetPath)] = md5_value
    return dict

def formData(data,absPath):
    resutl = {}
    for k,v in data.items():
        if k.startswith(absPath):
            newKey = k[len(absPath):]
            resutl[newKey] = v

    return resutl

# 发送kafka
@logger.catch
def start_producer(host, topic, msg, key):
    producer = KafkaProducer(bootstrap_servers=host,value_serializer =lambda k: json.dumps(k).encode(), key_serializer=lambda k: json.dumps(k).encode())
    # 同一个key值，会被送至同一个分区
    future = producer.send(topic, value=msg, key=key)
    try:
        future.get(timeout=10)
        # 监控是否发送成功
    except Exception as e:
        print(str(e))

@logger.catch
def start_producer_file(host, topic, msg, key):
    producer = KafkaProducer(bootstrap_servers=host, key_serializer=lambda k: json.dumps(k).encode())
    # 同一个key值，会被送至同一个分区
    future = producer.send(topic, value=msg, key=key)
    try:
        future.get(timeout=10)
        # 监控是否发送成功
    except Exception as e:
        print(str(e))


# 接收kafka
@logger.catch
def receiveData(conf):
    consumer = KafkaConsumer(bootstrap_servers=conf["kafka"]['host'], group_id=conf["kafka"]['groupid'])

    print('consumer start to consuming...')
    consumer.subscribe((conf["kafka"]["deference"]['topic']))

    sendConfig = conf["kafka"]["file"]
    for message in consumer:
        msg = json.loads(str(message.value, encoding="utf-8"))
        if msg.get("targetDir") is not None and msg.get("absDirPath") is not None and msg.get("data") is not None:
            absDirPath = msg["absDirPath"]
            targetDir = msg["targetDir"]
            for k,v in msg["data"].items():
                readPath = absDirPath+k
                if not os.path.exists(readPath):
                    logger.info("路径不存在"+readPath)
                    continue
                fileByte = readbin(readPath)
                filePath = targetDir+k
                start_producer_file(conf["kafka"]['host'], sendConfig["topic"], fileByte,filePath)



if __name__ == '__main__':
    logger.add('../logs/syncDaemon_{time:YYYY-MM-DD}.log',

               level='DEBUG',

               format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',

               rotation="00:00", retention="30 days")

    argv = sys.argv
    if len(argv)!=3:
        logger.info("python3 synced-dir-bot <dir> <targetDir>")
        print("python3 synced-dir-bot <dir> <targetDir>")
        sys.exit()

    # 判断文件夹是否存在
    if  not os.path.exists(argv[1]):
        logger.info("directory is not exists")
        print("directory is not exists")

    dir = argv[1]
    abspathDir = os.path.abspath(dir)

    targetDir = argv[2]


    fileList = dirFilesPath(dir)

    sendData = {}
    localHose = getFileMd5(fileList,abspathDir,targetDir)


    print(localHose)

    sendData["data"] = json.loads(json.dumps(formData(localHose,targetDir)))
    sendData["targetDir"] = targetDir
    sendData["absDirPath"] = abspathDir

    yamlConfig = readYamlConfig("syncing.yaml")

    start_producer(yamlConfig["kafka"]["host"],yamlConfig["kafka"]["checksum"]["topic"],sendData,"checksum")
    receiveData(yamlConfig)
