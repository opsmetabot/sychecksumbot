import yaml
import etcd3
import sys
import hashlib

# 加载yaml文件
def readEtcdCofig(configName):
    with open(configName) as ya:
        cfg = yaml.safe_load(ya)
        return cfg


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


def getFileMd5Value(filePath):

    try:
        md5_value = hashlib.md5(open(filePath, 'rb').read()).hexdigest()
        return md5_value
    except FileNotFoundError:
        return "null"

def readEtcdChecksum(prefix,etcd):
    records =  etcd.get_prefix(prefix)
    etcdChecksum = {}
    for record in records:
        key = record[1].key.decode('utf-8')
        etcdChecksum[key] = getFileMd5Value(key)
    return etcdChecksum


if __name__ == '__main__':
    argv = sys.argv
    prefix = "/"
    if len(argv)>=2:
        prefix = argv[1]
    else:
        print("usage: python3 file-checksum-console.py <prefix>")
        sys.exit()

    etcdConfig = readEtcdCofig("etcdConfig.yaml")
    etcdConnect  = connectEtcd(etcdConfig)

    prefixChecksum = readEtcdChecksum(prefix,etcdConnect)

    printEtcdChecksum(prefixChecksum)
