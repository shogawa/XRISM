#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh
mkdir -p pfiles
export PFILES="./pfiles;$HEADAS/syspfiles"

infile=$1
outfile=$2
grouptype=$3
groupscale=$4
#backfile=$4
#respfile=$5

ftgrouppha infile=$infile outfile=$outfile grouptype=$grouptype groupscale=$groupscale #backfile=$backfile respfile=$respfile

rm -rf pfiles