#!/bin/sh

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh
pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

infile=$1
outfile=$2
backfile=$3
respfile=$4

ftgrouppha infile=$infile backfile=$backfile respfile=$respfile outfile=$outfile grouptype=opt

rm -rf $pfiles_dir