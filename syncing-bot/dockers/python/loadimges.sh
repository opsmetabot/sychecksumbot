#!/bin/bash
docker load < ./python.sync.tar
docker tag e0fbb0237519 python3:sync
