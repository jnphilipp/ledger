# ledger

Web based ledger system to keep track of your money.

## Features
* run as systemd service
* detailed statistics
* budget view
* attach files to entries or accounts, for invoics, statements, ...

## Install

* from Source: ```make install```
* deb-Package: ```make deb```

To enable systemd service on startup:

```
systemctl --user enable ledger.service
```


## Update

### Version 2.1.0

* Manual database update required:
```
UPDATE ledger_file SET file = substr(file, 10) WHERE file LIKE 'accounts/%';
```
* Move folders in `APP_DATA_DIR/media/accounts` to `APP_DATA_DIR`
