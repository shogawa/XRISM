#!/bin/sh

obsid=$1
ln -si ../resolve/event_cl/${obsid}rsl_p0px1* .
ln -sf ../resolve/event_uf/${obsid}rsl_px1000_exp.gti.gz .
ln -sf ../auxil/${obsid}.ehk.gz .

cat <<EOF > region_RSL_det.reg
physical
+box(4,1,5,1.00000000)
+box(3.5,2,6,1.00000000)
+box(3.5,3,6,1.00000000)
+box(3.5,4,6,1.00000000)
+box(3.5,5,6,1.00000000)
+box(3.5,6,6,1.00000000)
EOF

cat <<EOF > region_RSL_det_27.reg
physical
+box(4,1,5,1.00000000)
+box(3.5,2,6,1.00000000)
+box(3.5,3,6,1.00000000)
+box(3,4,5,1.00000000)
+box(3.5,5,6,1.00000000)
+box(3.5,6,6,1.00000000)
EOF
