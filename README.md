# YouVCR

This program automatically records live streams from channels you specify as they are broadcasted.

## Usage

* Install dependencies.  
  `pip3 -r requirements.txt`
* Copy `config.example.yaml` to `config.yaml`, then you can add your faviourite channels to config file:  
  For each channel, you need a channel ID and a directory path for the files to be saved into.  
  To obtain the channel ID, copy the last part of the URL of the channel, e.g. the channel ID for `https://www.youtube.com/channel/UCoSrY_IQQVpmIRZ9Xf-y93g` is `UCoSrY_IQQVpmIRZ9Xf-y93g`.
* Execute `python3 main.py`, then keep it running for as long as you want the live streams to be recorded.  
  Or you may use the systemd service file provided below. (Please change `WorkingDirectory` and `/usr/bin/python3` accordingly)

```
[Unit]
Description=YouVCR
After=network-online.target

[Service]
WorkingDirectory=XXXXXXXXXX
ExecStart=/usr/bin/python3 main.py

RestartSec=5
Restart=always

[Install]
WantedBy=multi-user.target
```
