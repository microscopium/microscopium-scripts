#!/usr/bin/env bash

infile=$1
outdir=$2

echo ====================\nUNZIPPING\n====================
unzip $infile -d $outdir

echo ====================\nCONVERTING\n====================
source activate cellom
created_name=`python -c "import sys; print(sys.argv[1].rsplit('_')[-1].rsplit('.')[0])" $infile`
cd $outdir
cellom2tif -c 2 $created_name ${created_name}-tif

echo ====================\nILLUMINATION\n====================
source activate mic3
for channel in d0 d1 d2; do
    for field in f00 f01 f02 f03 f04 f05; do
        mic illum -s illum${field}${channel}.tif \
                  -r 41 -L 0.001 -q 0.95 -c 2 \
                  AS_*${field}${channel}.tif
    done
done

echo ====================\nSTITCHING\n====================
mic montage *.illum.tif -c 2 -o "[[2, 3, 4], [1, 0, 5]]" -O "[1, 2, 0]"
