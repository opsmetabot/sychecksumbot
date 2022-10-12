# 脚本执行顺序

1. receiveKafka.py 接收etcd 消息 并保存etcd
2. compareEtcdCheckSum.py 比对本地文件和etcd 区别，将差异的etcd 发送回去
3. receiveSyncFile.py 接收同步文件内容并保存