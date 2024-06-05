#!/bin/sh

export HEADAS=$TOOLS/heasoft/XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31
. $HEADAS/headas-init.sh
pfiles_dir=pfiles
mkdir -p $pfiles_dir
export PFILES="`pwd`/${pfiles_dir};$HEADAS/syspfiles"

srcfile=$1
bkgfile=$2
rmffile=$3
arffile=$4

fparkey $bkgfile $srcfile BACKFILE
fparkey $rmffile $srcfile RESPFILE
fparkey $arffile $srcfile ANCRFILE

rm -fr $pfiles_dir