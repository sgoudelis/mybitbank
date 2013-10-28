#mybitbank  
---
Your Personal CryptoCoin Bank

### Required setup

You should update pip and install project requirements.

```
easy_install --upgrade pip
pip install -r requirements.txt
```

### Configuration

Copy template file `mybitbank/settings-template.py` into `mybitbank/settings.py`.

Copy teamplate file `connections/config-template.py` into ` connections/config.py`

Edit file `mybitbank/settings.py` and setup your db connection. _(TODO: more details)_

Then run `./manage.py syncdb` to create the necessary tables.

Add your daemons in ` connections/config.py` _(TODO: more details)_