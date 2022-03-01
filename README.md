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
