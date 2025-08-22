#!/bin/sh

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