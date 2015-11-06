#!/bin/sh
for i in `seq 1 100` ; do
    ./a.out -v $i
    sleep 1
done
