## Activate
```
source activate.sh
```

## Products excluding pixel 12 (=calibration pixel) and 27
```
sh rsl_products.sh /path/to/00016200/analysis xa000162000
```

## Products excluding pixel 12 (=calibration pixel) and 27 and removing Ls from event file
```
sh rsl_products_Ls.sh /path/to/00016200/analysis xa000162000
```

## Products pixel by pixel
after making basic products
```
sh rsl_products_pix.sh /path/to/00016200/analysis xa000162000
```