#!/bin/sh
## this tool used to put config file checksum to etcd as well as 
## to send them to kafka


cd ../../scripts
python3 sync-etcd.py -f ../data/demo.smallsaas.cn-fileList.config --prefix /demo.smallsaas.cn

