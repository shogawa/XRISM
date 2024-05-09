#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh
mkdir -p pfiles
export PFILES="./pfiles;$HEADAS/syspfiles"

srcfile=$1
bkgfile=$2
rmffile=$3
arffile=$4

fparkey $bkgfile $srcfile BACKFILE
fparkey $rmffile $srcfile RESPFILE
fparkey $arffile $srcfile ANCRFILE

rm -fr pfiles