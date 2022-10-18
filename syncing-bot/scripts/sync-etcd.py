import etcd3
import hashlib
import os
import yaml
import sys
from loguru import logger


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
def connectEtcd(cfg):
    host = cfg['etcd']['host']
    port = cfg['etcd']['port']
    password = cfg['etcd']['password']
    etcd = etcd3.client(host, port)
    return etcd


@logger.catch
def getFileMd5(filename):
    # test的文件路径
    dict = {}
    for root, dirs, files in os.walk(filename):
        for file in files:
            file_path = os.path.join(root, file)
            md5_value = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
            dict[file_path] = md5_value
    return dict


@logger.catch
def getFileMd5Value(fileList):
    dict = {}
    if fileList != None:
        for key in fileList:
            key = key.strip()
            try:
                md5_value = hashlib.md5(open(key, 'rb').read()).hexdigest()
                dict[key] = md5_value
            except FileNotFoundError:
                dict[key] = "null"
                continue
    return dict

@logger.catch
def setEtcdValue(dict, etcd):
    for key, value in dict.items():
        logger.info("同步文件checksum"+"--"+key+"---"+value)
        etcd.put(key, value)


if __name__ == '__main__':

    logger.add('../logs/sync-etcd_{time:YYYY-MM-DD}.log',

               level='DEBUG',

               format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {file} - {line} - {message}',

               rotation="00:00", retention="30 days")

    logger.info('sync-etcd日志')
    argv = sys.argv

    if len(argv) < 2:
        logger.info("参数错误" + argv)
        print("python3 etcdScript <fileList>")
        sys.exit()

    cfg = readEtcdCofig("syncing.yaml")
    etcd = connectEtcd(cfg)

    # 改为指定的 fileList
    fileList = argv[1]
    logger.info("读入文件列表"+"--"+argv[1])

    data = getFileMd5Value(realFile(fileList))
    setEtcdValue(data, etcd)
