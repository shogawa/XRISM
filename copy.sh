mkdir analysis

cd analysis
obsid=$1
ln -sf ../resolve/event_cl/${obsid}rsl_p0px1* .
ln -sf ../resolve/event_uf/${obsid}rsl_px1000_exp.gti.gz .
ln -sf ../auxil/${obsid}.ehk.gz .
ln -sf ../xtend/event_cl/${obsid}xtd_p0300* .
ln -sf ../xtend/event_uf/${obsid}xtd_p0300*.bimg.gz .
ln -sf ../xtend/event_uf/${obsid}xtd_p0300*.fpix.gz .
ln -sf ../xtend/event_cl/${obsid}xtd_p031* .
ln -sf ../xtend/event_uf/${obsid}xtd_p031*.bimg.gz .
ln -sf ../xtend/event_uf/${obsid}xtd_p031*.fpix.gz .


cp $HEADAS/refdata/region_RSL_det.reg .

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

cat <<EOF > exclude_calsources.reg
physical
-circle(920.0,1530.0,92.0)
-circle(919.0,271.0,91.0)
EOF
