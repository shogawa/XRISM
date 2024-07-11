# XRISM Data Reduction Tools
These scripts are based on the following:
* [XRISM Quick-Start Guide v2.1](https://xrism-c2c.atlassian.net/wiki/spaces/XRISMPV/pages/137199656/Data+reduction+and+analysis+tips)
* [Things to watch out for in pipeline-processed data](https://xrism-c2c.atlassian.net/wiki/spaces/XRISMPV/pages/140869909)
* [xrism_sdc_tutorial_20240306_all_v5.pdf](https://xrism-c2c.atlassian.net/wiki/spaces/XRISMPV/pages/140869909)

## How to use it
```
python resolve.py -oi [OBSID] -fi [Filter ID] -wr [RMF size] -ed [/path/to/eventfile] -pd [/path/to/products]
python xtend.py -oi [OBSID] -dc [dataclass] -ed [/path/to/eventfile] -pd [/path/to/products]
```
e.g.,
```
wget -nv -m -np -nH --cut-dirs=6 -R "index.html*" --execute robots=off --wait=1 https://data.darts.isas.jaxa.jp/pub/xrism/data/obs/rev3/0/000162000/
./decrypt_data.pl -r -d 000162000 -p PGPKEY
mkdir -p 00016200/products
python resolve.py -oi xa000162000 -fi 1000 -wr S -ed 00016200 -pd 00016200/products
python xtend.py -oi xa000162000 -dc 31100010 -ed 00016200 -pd 00016200/products
```

## Premise
```
000162000
├── products
├── auxill
├── log
├── resolve
└── xtend
```

## Setting
The followings should be changed:
```
HEADAS = '/home/ogawa/work/tools/heasoft/XRISM_20Jun2024_Build8/x86_64-pc-linux-gnu-libc2.31'
CALDB = '/home/ogawa/work/tools/caldb'
XSELECT_MDB = '/home/ogawa/work/tools/heasoft/xrism/xselect.mdb.xrism'
rmfparamfile = '/home/ogawa/work/tools/heasoft/xrism/xa_rsl_rmfparam_20190101v006.fits.gz'
instmap = '/home/ogawa/work/tools/heasoft/xrism/xa_xtd_instmap_20190101v004.fits'
```
