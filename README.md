# mybitbank  

## Your Personal CryptoCoin Bank (for bitcoin, litecoin, feathercoin, ppcoin, namecoin, dogecoin, auroracoin and more)

**MISSION STATEMENT:** Do you want to be in charge of your bitcoin/altcoin safekeeping in your own self-hosted bank? Mybitbank was made with the intention of providing access to the functionality of bitcoind and others through a web interface, deployed in a home server environment, isolated from larger networks. Your rules, your responsibility. 

**Visit the Reddit UBER-MEGA thread [here](http://www.reddit.com/r/Bitcoin/comments/27v3mw/i_just_released_mybitbank_project_on_github/ "Reddit").**

[![Build Status](https://travis-ci.org/sgoudelis/mybitbank.svg?branch=master)](https://travis-ci.org/sgoudelis/mybitbank)

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
12. Provision for unresponsive xxxcoind instances
13. Support wallets with passphrases

### Screenshots


#### Dashboard
![Alt text](/doc/dashboard-screen.jpg "Dashboard")

#### Accounts
![Alt text](/doc/accounts-screen.jpg "Accounts")

#### Transactions
![Alt text](/doc/transactions-screen.jpg "Transaction")

#### Transfer
![Alt text](/doc/transfer-screen.jpg "Transfer")


### Todos

1. Proper settings page (for adding/editing xxxcoind instance parameters)
2. Proper account details page and preferences
3. Add aliasing support for accounts
4. Add transfer fee in transfer dialog page
5. Add two-factor authentication (?)
6. Support client-side raw transaction generation
7. Internationalization
8. Support for multisig addresses

### Security concerns 

1. When seting up, consider using a different account to run your xxxcoinds. Using your desktop account to run bitcoind may not be wise.
2. Adding passphrases in wallets is highly advised. Mybitbank supports passphrases.
3. Avoid using the built-in web server provided by Django for production environments. Please see in the apache/ folder for sample configs to setup mybitbank on Apache.
4. Setup your Apache deployment with SSL/HTTPS. Mybitbank will complain if it detects that you are not over SSL/HTTPS.

### Known issues

1. When any of the coin instances (bitcoind, litecoind, etc) is downloading blocks, the instance becomes unresponsive for some time. During this time the page will also appear to hang but only for 10 seconds. After 10 seconds (configurable) of timeout the page will disable the coin service for another 10 seconds. This happens so that subsequent calls to the same coin service will be ignored for those 10 seconds, speeding up the page load times. 



### Installation on Ubuntu 13.04 (and probably other versions as well)

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

Checkout latest stable branch (use master for now)

```
git checkout origin/master
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

Or just do a:

```
pip install -r requirements.txt
```

The above will install all needed components.


#### Install GeoIP

Django supports GeoIP but its implementation is just a wrapper. The libgeoip library still needs to be installed system-wide.

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

You can start up the Django development web server (not recommended for production deployments) to test your deployment.

```
python ./manage.py runserver localhost:8000
```

Visit the page http://localhost:8000/



#### Apache configuration

Please take a look at the apache/ folder for a sample configuration to run mybitbank as a WSGI application. Take care to update the directory paths in the config files.

---

## Licence

mybitbank is a free software distributed under the terms of the MIT license

## Donations

You can send donations here:

**BTC** to **1398vTCqE8gjmmDq9Cw3Z94V3oxbe8bW4o**  
**LTC** to **LYGoNiZGC1vvq9SoVo3o3Ru8gML8XPCrBe**

