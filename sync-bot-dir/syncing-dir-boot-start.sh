#!/bin/bash

# 1. 检查程序的运行状态，避免重复启动
## 1.1 ps -ef | grep  python | grep "APScheduler"  得到 python 脚本上的含用 APScheduler命令的进程，
## 1.2 grep -v grep 排除当前脚本命令的进程
## 1.3 awk '{print $2}'  得到  APScheduler 进程的进程ID
kill_pid=`ps -ef | grep  python | grep "syncing-dir-bot"  |grep -v grep | awk '{print $2}'`

# 判断进程是否存在，如果存在，则不在再重复执行
if [ -n "${kill_pid}" ]
then
    echo "pid = "${kill_pid}
    echo "syncing-dir-bot.py 程序正在运行中，请勿重复启动"
    exit 1
fi

# 2. nohup  后台运行脚本
nohup python3 ./syncing-dir-bot.py >nohup.out   2>&1 &

# 3. 显示日志
tail -200f ./nohup.out
