#!/bin/sh

pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

infile=$1
outfile=$2
grouptype=$3
groupscale=$4
#backfile=$4
#respfile=$5

ftgrouppha infile=$infile outfile=$outfile grouptype=$grouptype groupscale=$groupscale #backfile=$backfile respfile=$respfile

rm -rf $pfiles_dir