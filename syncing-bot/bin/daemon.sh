#!/bin/sh
## this tool used to start a kafka client daemon to 
## listen and handle the kafka syncing message for file content

# cd ./scripts
# python3 ./syncDaemon.py

opt=$1
if [ ! $opt ];then
  echo 'usage: daemon <start|stop>'
  exit -1
fi

startbot() {
   docker run -d --rm --name syncingbot -v ${PWD}/../scripts:/scripts -w /scripts python3:sync  python3 syncDaemon.py  
}

stopbot() {
   docker stop syncingbot
}


## start docker 

if [ $opt == start ];then
  startbot
else
  stopbot
fi

