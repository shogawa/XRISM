#!/bin/sh

export TOOLS=/home/ogawa/work/tools

export HEADAS=$TOOLS/heasoft/XRISM_20Jun2024_Build8/x86_64-pc-linux-gnu-libc2.31

. $HEADAS/headas-init.sh

export CALDB=$TOOLS/caldb
. $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=$TOOLS/heasoft/xrism/xselect.mdb.xrism