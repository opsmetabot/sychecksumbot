#!/bin/bash

# 查询程序，并得到 pid
kill_pid=`ps -ef | grep  python | grep "synced-dir-bot"  |grep -v grep | awk '{print $2}'`
echo "pid = "${kill_pid}

# kill , 关闭进程
if [ -n "${kill_pid}" ]
then
    kill -9 ${kill_pid}
    echo "进程已 kill 成功"
else
	echo "进程 pid：${kill_pid} 不存在！"
fi