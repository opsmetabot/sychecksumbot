import etcd3
import hashlib
import os
import yaml

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


def getFileMd5(filename):
    # test的文件路径
    dict = {}
    for root, dirs, files in os.walk(filename):
        for file in files:
            file_path = os.path.join(root, file)
            md5_value =  hashlib.md5(open(file_path,'rb').read()).hexdigest()
            dict[file_path] = md5_value
    return dict

def getFileMd5Value(fileList):
    dict = {}
    if fileList !=None:
        for key in fileList:
            key = key.strip()
            try:
                md5_value = hashlib.md5(open(key, 'rb').read()).hexdigest()
                dict[key] = md5_value
            except FileNotFoundError:
                dict[key] = "null"
                continue
    return dict

def setEtcdValue(dict,etcd):
    for key,value in dict.items():
        etcd.put(key,value)

if __name__ == '__main__':
    cfg = readEtcdCofig("etcdScript.yaml")
    etcd = connectEtcd(cfg)
    fileList = cfg["fileList"]["path"]
    data  = getFileMd5Value(realFile(fileList))
    setEtcdValue(data,etcd)
