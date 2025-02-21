SteamSpy
--------
Silent Recon Tool for checking steam users who are online/offline.
This used to be an old script I had from 2023 that I remodified & modernized.

## Features
- Built-in Asynchronous Tor Library froked from stem as long as tor.exe is mapped as 
a path enviornment variable if your own windows.
- Exteremely Minimal Amounts of Code
- Scraping Target's Friends
- Seeing if User is a Private Account
- Scraping User's Profile Picture in all it's glory.
- Running as your own seperate python library,
such as using a webhook to track a user, (take whatever code your looking for.)
- There are no sign ups to using this tool.

## TODOS
- Track Game User is playing on if user is online

## How to install
- You need Python 3.9 or higher, the restirictions are very minimal.
```
pip install -r requirements.txt
```

## How to use 
```
cli.py --help
```

# What to do if Errors are Encountered

## Site Starts Acting Funny
- Get a proxy or configure tor to fix it up Otherwise Replace or add in new user-agents to the useragents script.


