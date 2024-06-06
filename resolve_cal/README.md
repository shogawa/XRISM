## Premise
```
mkdir -p analysis/Fe55
cd Fe55
```
<pre>
000162000
├── analysis
│   └── Fe55
├── auxill
├── log
├── resolve
└── xtend
</pre>

## Hp spectrum in from Fe55 Filter
```
sh rsl_calspec.sh xa000162000
```

## Pixel by pixel Hp spectrum in from Fe55 Filter
```
sh rsl_calspec_pix.sh xa000162000
```

## Fitting Mn K\alpha
```
xspec
@rsl_fitfe55.xcm
```
or
```
python -t "Circinus galaxy" -sf xa000162000rsl_fe55.pha -rf newdiag.rmf
```
