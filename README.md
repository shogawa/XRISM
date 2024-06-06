# XRISM Products Tools
These scripts are based on the following:
* [XRISM Quick-Start Guide v2.1](https://xrism-c2c.atlassian.net/wiki/spaces/XRISMPV/pages/137199656/Data+reduction+and+analysis+tips)
* [Things to watch out for in pipeline-processed data](https://xrism-c2c.atlassian.net/wiki/spaces/XRISMPV/pages/140869909)
* [xrism_sdc_tutorial_20240306_all_v5.pdf](https://xrism-c2c.atlassian.net/wiki/spaces/XRISMPV/pages/140869909)

## How to use it
```
wget -nv -m -np -nH --cut-dirs=6 -R "index.html*" --execute robots=off --wait=1 https://data.darts.isas.jaxa.jp/pub/xrism/data/obs/rev3/0/000162000/
./decrypt_data.pl -r -d 000162000 -p PGPKEY
mkdir -p 00016200/analysis
sh rsl_products.sh /path/to/00016200/analysis xa000162000
sh xtd_products.sh /path/to/00016200/analysis xa000162000 31100010
```

## Premise
<pre>
$TOOLS
├── heasoft
│   ├── XRISM_15Oct2023_Build7
│   └── xrism
│       ├── xa_xtd_instmap_20190101v004.fits
│       └── xselect.mdb.xrism
└── caldb
    ├── data
    │   ├── gen
    │   ├── and
    │   ├── prelaunch_ah
    │   └── xrism
    └── software
        └── tools
            ├── alias_config.fits
            ├── caldb.config
            ├── caldbinit.csh
            └── caldbinit.sh

000162000
├── analysis
├── auxill
├── log
├── resolve
└── xtend
</pre>

## Setup
If XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31 is changed:
```
find . -type f -name '*.sh' -exec sed -i '' -e 's[XRISM_15Oct2023_Build7/x86_64-pc-linux-gnu-libc2.31[XRISM_15Oct2023_Build8/x86_64-pc-linux-gnu-libc2.31[g' {} +;
```