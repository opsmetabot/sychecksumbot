from kafka import KafkaProducer, KafkaConsumer
import json
import yaml
import struct
import sys
from loguru import logger


@logger.catch
def readEtcdCofig(configName):
    with open(configName) as ya:
        cfg = yaml.safe_load(ya)
        return cfg

@logger.catch
def read_bin(file_name):
    with open(file_name, "rb") as f:
        f_content = f.read()
        content = struct.unpack("B" * len(f_content), f_content)
        f.close()
    return content

@logger.catch
def readbF(upfile):
    try:
        with open(upfile, "rb") as fp:
            file1 = fp.read()
        return file1
    except FileNotFoundError:
        return b"null"

@logger.catch
def start_producer(host, topic, msg, key):
    producer = KafkaProducer(bootstrap_servers=host, key_serializer=lambda k: json.dumps(k).encode())
    # 同一个key值，会被送至同一个分区
    future = producer.send(topic, value=msg, key=key)
    try:
        future.get(timeout=10)
        # 监控是否发送成功
    except Exception as e:
        print(str(e))

@logger.catch
def receiveData(conf,prefix):
    consumer = KafkaConsumer(bootstrap_servers=conf["receive"]['host'], group_id=conf["receive"]['groupid'])

    print('consumer start to consuming...')
    consumer.subscribe((conf["receive"]['topic']))

    sendConfig = conf["send"]

    print(prefix)
    for message in consumer:
        if message.key != None:
            key = message.key.decode("utf-8").strip()
            if key == "\"syncFile\"":
                msg = json.loads(json.loads(message.value.decode("utf-8")))
                for k, v in msg.items():
                    readPath = k[len(prefix):]
                    r = readbF(readPath)
                    print(readPath)
                    logger.info("同步文件名："+readPath)
                    start_producer(sendConfig["host"], sendConfig["topic"], r, k)


if __name__ == '__main__':

    logger.add('../logs/syncDaemon_{time:YYYY-MM-DD}.log',

               level='DEBUG',

               format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',

               rotation="00:00", retention="30 days")

    argv = sys.argv
    cfg = readEtcdCofig("syncing.yaml")
    kafka = cfg["kafka"]
    if len(argv)<2:
        logger.info("参数错误" + argv)
        print("python3 syncFiles.py <prefix>")
        sys.exit()
    prefix = argv[1]

    logger.info("prefix"+prefix)

    print(prefix)
    receiveData(kafka,prefix)
