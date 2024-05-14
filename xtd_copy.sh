#!/bin/sh

obsid=$1
ln -sf ../auxil/${obsid}.ehk.gz .
ln -sf ../xtend/event_cl/${obsid}xtd_p0300* .
ln -sf ../xtend/event_uf/${obsid}xtd_p0300*.bimg.gz .
ln -sf ../xtend/event_uf/${obsid}xtd_a0300*.fpix.gz .
ln -sf ../xtend/event_cl/${obsid}xtd_p031* .
ln -sf ../xtend/event_uf/${obsid}xtd_p031*.bimg.gz .
ln -sf ../xtend/event_uf/${obsid}xtd_a031*.fpix.gz .

cat <<EOF > exclude_calsources.reg
physical
-circle(920.0,1530.0,92.0)
-circle(919.0,271.0,91.0)
EOF
