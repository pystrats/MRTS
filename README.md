A futures portfolio that takes long positions in contracts if implied yield is lower than 0% (long backwardation) and short positions if implied yield is higher than 15% (short contango), with a maximum of one position per futures chain, favoring steeper yields. A portfolio aims for a target gross notional exposure of 200% at equal weights.

# Installation
```
$ git clone https://github.com/pystrats/mrts.git
$ cd mrts
$ pip install .
```

# Usage
```
$ mrts [ACCOUNT_VALUE_IN_USD]
```
Example:
```
$ mrts 10000000
```
