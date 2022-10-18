#!/bin/sh

# ssh -p 6122 root@172.17.0.1 \
cd /data/jfeat/syncing-bot/bin && sh sync-checksum.sh && sh daemon.sh start

