#!/bin/sh

cd sync-parts
for line in $(ls);do
   echo $line
   sh $line
done

