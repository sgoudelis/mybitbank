# mybitbank  
---
Your Personal CryptoCoin Bank

### Required setup

You should update pip and install project requirements.

```
easy_install --upgrade pip
easy_install base58
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