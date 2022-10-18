#!/bin/sh
## this tool used to put config file checksum to etcd 

cd ../../scripts
python3 sync-etcd.py -f ../data/fileList.config --prefix /desk.hdqmjs.com

