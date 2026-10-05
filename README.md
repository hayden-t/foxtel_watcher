# foxtel_watcher
Automatically plays a chosen channel from watch.foxtel.com.au in the browser, fullscreen, from boot and maintains under linux.

Requires Chrome with "User-Agent Switcher and Manager" extension installed and activated for all tabs as "windows 10"
```
chrome://extensions/?id=bhchdcejhohfmigjafbampogmaanbfkg
```

Requires supervisor for autostart/restart, link supervisor scripts from repo into etc to create workers and loggers, edit paths here and in the linked scripts as need:
```
ln -s /home/user/foxtel_watcher/supervisor.control.conf /etc/supervisor/conf.d/supervisor.control.conf
ln -s /home/user/foxtel_watcher/supervisor.player.conf /etc/supervisor/conf.d/supervisor.player.conf
```
create .env file in base dir with foxtel subscription logins:
```
FOXTEL_USERNAME=email
FOXTEL_PASSWORD=password
```

Inspired and forked from https://github.com/coxy86/iptv
The content is paid for (I wouldnt, but people do), this is not pirating, foxtel blocking linux & firefox is arbitrary and imo antitrust.
