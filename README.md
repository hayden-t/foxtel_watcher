# Foxtel Watcher
Automatically plays a chosen channel from watch.foxtel.com.au in the browser, fullscreen, from boot and maintains under linux.

Requires Chrome with "User-Agent Switcher and Manager" extension installed and activated for all tabs as "windows 10"
```
chrome://extensions/?id=bhchdcejhohfmigjafbampogmaanbfkg
```

Requires supervisor for autostart/restart, link supervisor scripts from repo into etc to create workers and loggers, edit paths here and in the linked scripts as need:
```
ln -s /home/user/foxtel_watcher/supervisor.player.conf /etc/supervisor/conf.d/supervisor.player.conf
ln -s /home/user/foxtel_watcher/supervisor.control.conf /etc/supervisor/conf.d/supervisor.control.conf
```
"player" launches a chrome instance with remote console access

"control" launches a selenium script that connects to chrome and navigates it to the channel specified in launch.py (edit as needed)

create .env file in base dir with foxtel subscription logins:
```
FOXTEL_USERNAME=email
FOXTEL_PASSWORD=password
CHANNEL_GENRE=Sports
CHANNEL_NUMBER=502
```
See https://watch.foxtel.com.au/en-AU/epg-fixture for the list of available genres (in the drop down) and the desired channel number. 

You might also like to have auto hide inactive cursor, put this in startup
```
unclutter -idle 5 -root
```

Inspired and based on https://github.com/coxy86/iptv

The content is paid for (I wouldnt, but people do), this is not pirating, foxtel blocking linux & firefox is arbitrary and imo antitrust.
