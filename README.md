# mybitbank  
---
Your Personal CryptoCoin Bank


### Features

1. Support multiple bitcoind (or other coins) instances at the same time (through a config file)
2. Tested altcoin instances: litecoin, ppcoin, namecoin, dogecoin, feathercoin, novacoin, auroracoin
3. View accounts, transactions for all coin types
4. Addressbook for easy access to addresses
5. Transfer coins 
6. Network map of connected peers with extra details
7. Built with bootstap layout
8. Mobile layout support through bootstrap
9. Aliases support for addresses. You keep forgeting addresses? Use an alias
10. Build on Django. Support for Django application accounts
11. Show balance in USD


### Todos

1. Proper settings page (for adding/editing xxxcoind instance parameters)
2. Proper account details page and preferences
3. Add aliasing support for accounts
4. Add transfer fee in transfer dialog page
5. many more

### Known issues

1. When any of the coin instances (bitcoind, litecoind, etc) is downloading blocks, the instance becomes unresponsive for some time. During this time the page will also appear to hang but only for 10 seconds. After 10 seconds (configurable) of timeout the page will disable the coin service for another 10 seconds. This happens so that subsequent calls to the same coin service will be ignored for those 10 seconds, speeding up the page load times.



### Instalation on ubuntu 13.04

Install git

```
sudo apt-get install git
```

Clone repository

```
git clone https://github.com/sgoudelis/mybitbank.git
```

Change directory

```
cd mybitbank
```

List brances

```
git branch -v -a
```

Checkout latest stable branch (now 0.1)

```
git checkout -b 0.1 origin/0.1
```

Install python-pip

```
sudo apt-get install python-pip
```

Install Django

```
sudo pip install django==1.5.4
```

You can use other methods to install Django of course. Currenlty Django 1.5.4 is the minimum requirement. 

Install south

```
sudo pip install south
```

Install python-dateutil

```
sudo apt-get install python-dateutil
```

Install GeoIP

Django supports GeoIP but its implementation is just a wrapper. The libgeoip library still needs to be install system-wide.

```
sudo apt-get install python-dev
sudo apt-get install libgeoip-dev
sudo pip install geoip
```

Then download GeoIP City datasets in binary format from [MaxMind](http://dev.maxmind.com/geoip/legacy/geolite/) uncompress and put them in `~/.geoip/` folder.
 

You may also need to comment out the following line in 'mybitbank/settings.py' if you are on Ubuntu, or keep it for Mac OS

GEOIP_LIBRARY_PATH = '/opt/local/lib/libGeoIP.dylib'

On Mac OS X, you can install using [homebrew](http://github.com/mxcl/homebrew):
```
brew install geoip
```
or [MacPorts](http://www.macports.org/install.php):
```
sudo port install libgeoip
```



### Configuration

Configure the Django settings.py file. Please configure as you see fit. This is a Django settings file.

Copy template file 'mybitbank/settings-template.py' into 'mybitbank/settings.py'.

```
cp mybitbank/settings-template.py mybitbank/settings.py
```

Also configure the database parameters in `mybitbank/settings.py`



Configure xxxcoind instances

Copy and configure a walletconfig.py file. This file contains parameters on where to find the xxxcoind instances (bitcoind, litecoind, etc.). Configure at your discretion.

```
cp mybitbank/libs/connections/walletconfig-template.py mybitbank/libs/connections/walletconfig.py
```

Configure Django application database parameters

Make sure that 'mybitbank/settings.py' has proper database parameters (if you are using sqlite3 make sure you define a filepath to the sqlite3 file). 

```
python ./manage.py syncdb
```

When asked to install a superuse, create one.

```
python ./manage.py migrate
```


---

## Licence

mybitbank is a free software distributed under the terms of the MIT license
