import yaml
import etcd3
import sys
import getopt
import os

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
def dirFilesPath(path):

    filePaths = []  # 存储目录下的所有文件名，含路径
    for root, dirs, files in os.walk(path):
        for file in files:
            filePaths.append(os.path.abspath(file))
    return filePaths

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
    argv = sys.argv
    etcdConfig = readEtcdCofig("syncing.yaml")
    etcdConnect  = connectEtcd(etcdConfig)

    try:
        options, args = getopt.getopt(sys.argv[1:], "hf:d:", ["help", "fileList=", "dir="])
    except getopt.GetoptError:
        sys.exit()

    if ("-f" in argv and "-d" in argv) and ("-f" not in argv or "-d" not in argv):
        print("python3 etcd-checksum-console.py [-f <fileList>|-d <dir>]")
        sys.exit()


    if(len(argv)<3):
        print("python3 etcd-checksum-console.py [-f <fileList>|-d <dir>]")
        sys.exit()

    fileListPath = ""

    # 修改命令行读取
    dir = ""

    for name, value in options:
        if name in ("-f", "--fileList"):
            fileListPath = value
        if name in ("-d","--dir"):
            dir = value

    if "-f" in argv:
        fileList = realFile(fileListPath)
    else:
        fileList = dirFilesPath(dir)


    checksumData =  readFileListChecksum(fileList,etcdConnect)
    printEtcdChecksum(checksumData)
