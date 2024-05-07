#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
source $HEADAS/headas-init.sh
mkdir -p pfiles
export PFILES="./pfiles;$HEADAS/syspfiles"

infile=$1
backfile=$2
respfile=$3

ftgrouppha infile=$infile backfile=$backfile respfile=$respfile outfile=ifile_optbin.pha grouptype=opt

rm -rf pfiles