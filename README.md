# Foxtel Watcher
Automatically plays a chosen channel from watch.foxtel.com.au (Foxtel Go) in the browser, fullscreen, from boot and monitors it under linux (debian in my case).

Requires Chrome with "User-Agent Switcher and Manager" extension installed and activated for all tabs as "windows 10", (with the browser worker running, install it from chrome store)
```
chrome://extensions/?id=bhchdcejhohfmigjafbampogmaanbfkg
```
You will also need the python libs listed in requirements.txt via pip/venv

Requires supervisor package for autostart/restart, link included supervisor scripts from repo into etc to create workers and log monitors, edit paths here and in the linked scripts to match yours:
```
ln -s /home/user/foxtel_watcher/supervisor.browser.conf /etc/supervisor/conf.d/supervisor.browser.conf
ln -s /home/user/foxtel_watcher/supervisor.controller.conf /etc/supervisor/conf.d/supervisor.controller.conf
```
"browser" launches a chrome instance with remote console access

"controller" launches a python script that connects to chrome and navigates it with selenium to the channel specified in .env (logging in if necessary)

create .env file in base dir with foxtel subscription logins, desired genre & channel:
```
FOXTEL_USERNAME=email
FOXTEL_PASSWORD=password
CHANNEL_GENRE=Sports
CHANNEL_NUMBER=502
```
See https://watch.foxtel.com.au/en-AU/epg-fixture for the list of available genres (in the drop down) and the desired channel number. 

You might also like to have auto hide inactive cursor, install unclutter package and put this in launcher startup
```
unclutter -idle 5 -root
```

Inspired and based on https://github.com/coxy86/iptv

All content is paid for (I wouldnt, but people do), this is not pirating, foxtel blocking linux & firefox is arbitrary and imo akin to antitrust.
