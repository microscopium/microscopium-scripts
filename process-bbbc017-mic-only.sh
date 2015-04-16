#!/usr/bin/env bash

datadir=$1

echo -e "====================\nILLUMINATION\n===================="
cd $datadir
source activate mic3
for channel in d0 d1 d2; do
    for field in f00 f01 f02 f03 f04 f05; do
        mic illum -s illum${field}${channel}.tif \
                  -r 41 -L 0.001 -q 0.95 -c 2 \
                  AS_*${field}${channel}.tif
    done
done

echo -e "====================\nSTITCHING\n===================="
mic montage *.illum.tif -c 2 -o "[[2, 3, 4], [1, 0, 5]]" -O "[1, 2, 0]"
