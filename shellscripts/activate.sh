#!/bin/sh

export HEADAS=/home/ogawa/work/tools/heasoft/XRISM_20Jun2024_Build8/x86_64-pc-linux-gnu-libc2.31

. $HEADAS/headas-init.sh

export CALDB=/home/ogawa/work/tools/caldb
. $CALDB/software/tools/caldbinit.sh

export XSELECT_MDB=/home/ogawa/work/tools/heasoft/xrism/xselect.mdb.xrism