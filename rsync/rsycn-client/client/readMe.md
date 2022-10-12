# 配置文件

### 生成配置文件列表

```
python3 getFileList.py 文件目录 生成文件列表文件 -a -f "过滤文件后缀" -n "只获取后缀为"
```

1. -f 和 -n 不能同时使用

2. -f 过滤文件后缀使用 | 隔开 

    ```
    python3 getFileList.py 文件目录 生成文件列表文件 -f ".jpg|.txt"
    ```

3. -a 追加文件 不填为全覆盖



### 配置etcd脚本

​	配置etcdScript.yaml文件

	1. fileList 为 文件列表文件 需要绝对路径
	1. etcd 配置etcd登录
	1. kafka 配置kafka 

​	

### 脚本执行

 	1. getFileList.py 生成文件列表文件
 	2. etcdScript.py 将文件列表的 checksum 存储到etcd中
 	3. sendKafaka.py 将文件列表的checksum 发送到kafka
 	4. syncFiles.py  如果kafka 那边检测到有不同文件 会传消息过来 将不同的文件传输回去(此脚本会一直监听，需要手动关闭)

​	