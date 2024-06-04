## How to use it
```
wget -nv -m -np -nH --cut-dirs=6 -R "index.html*" --execute robots=off --wait=1 https://data.darts.isas.jaxa.jp/pub/xrism/data/obs/rev3/0/000162000/
./decrypt_data.pl -r -d 000162000 -p PGPKEY
mkdir -p 00016200/analysis
sh rsl_products.sh /path/to/00016200/analysis xa000162000
sh xtd_products.sh /path/to/00016200/analysis xa000162000 31100010
```
