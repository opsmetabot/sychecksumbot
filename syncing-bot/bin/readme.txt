1. run daemon.sh first to run a service to mon. the kafka message
2. run sync-parts.sh to sync all the scripts within sync-parts  
3. when syncing checksum done, send the checksum data saved in etcd to the remote kafka

## all above steps will be executed via cron in syncingcron docker  
## or the same if manually run 

