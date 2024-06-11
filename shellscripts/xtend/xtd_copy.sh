#!/bin/sh

obsid=$1
ln -sf ../auxil/${obsid}.ehk.gz .
ln -sf ../xtend/event_cl/${obsid}xtd_p0* .
ln -sf ../xtend/event_uf/${obsid}xtd_p0*.bimg.gz .
ln -sf ../xtend/event_uf/${obsid}xtd_a0*.fpix.gz .

cat <<EOF > exclude_calsources.reg
physical
-circle(920.0,1530.0,92.0)
-circle(919.0,271.0,91.0)
EOF
