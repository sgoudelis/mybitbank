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
5. 



### Required setup

You should update pip and install project requirements.

```
easy_install --upgrade pip
pip install -r requirements.txt
```

#### GeoIP

Install the GeoCity C library. You can get it from [MaxMind](http://www.maxmind.com/app/c).

On Mac OS X, you can install using [homebrew](http://github.com/mxcl/homebrew):
```
brew install geoip
```
or [MacPorts](http://www.macports.org/install.php):
```
sudo port install libgeoip
```


Download GeoIP City datasets in binary format from [MaxMind](http://dev.maxmind.com/geoip/legacy/geolite/) uncompress and put them in `.geoip/` folder.

```
cd .geoip
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
gzip -d GeoLiteCity.dat.gz
```


### Configuration

Copy template file `mybitbank/settings-template.py` into `mybitbank/settings.py`.

Copy teamplate file `connections/config-template.py` into ` connections/config.py`

Edit file `mybitbank/settings.py` and setup your db connection. _(TODO: more details)_

Then run `./manage.py syncdb` to create the necessary tables.

Add your daemons in ` connections/config.py` _(TODO: more details)_


---

## Licence

mybitbank is a free software distributed under the terms of the MIT license
