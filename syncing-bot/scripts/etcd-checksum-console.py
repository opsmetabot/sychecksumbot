import yaml
import etcd3
import sys

# 加载yaml文件
def readEtcdCofig(configName):
    with open(configName) as ya:
        cfg = yaml.safe_load(ya)
        return cfg

# 读取文件列表
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

# 读取etcd 配置文件 并连接etcd
def connectEtcd(cfg):
    host = cfg['etcd']['host']
    port = cfg['etcd']['port']
    password = cfg['etcd']['password']
    etcd = etcd3.client(host,port)
    return etcd

# 打印etcd 的checksum
def printEtcdChecksum(checksumList):
    for k,v in checksumList.items():
        print("path:",k,"----","checksum:",v)

def readEtcdChecksum(prefix,etcd):
    records = etcd.get_prefix(prefix)
    oldEtcdData = {}
    for record in records:
        key = record[1].key.decode('utf-8')
        value = record[0].decode('utf-8')
        oldEtcdData[key] = value
    return oldEtcdData

#读取文件列表的chckesum
def readFileListChecksum(fileList,etcd):
    checksumData = {}
    for filePath in fileList:
        key = filePath.strip()
        record = etcd.get(key)
        value = record[0]
        if record[0] != None:
            checksumData[key] = record[0].decode('utf-8')
        else:
            checksumData[key] = "null"
    return checksumData


if __name__ == '__main__':
    etcdConfig = readEtcdCofig("syncing.yaml")
    etcdConnect  = connectEtcd(etcdConfig)

    argv = sys.argv
    if(len(argv)<2):
        print("python3 etcd-checksum-console.py <fileList>")
        sys.exit()
    fileListPath = argv[1]
    fileList = realFile(fileListPath)

    checksumData =  readFileListChecksum(fileList,etcdConnect)
    printEtcdChecksum(checksumData)
