# web_scrobbler.py
## Description

web_scrobbler.py is a simple Python script for scrobbling music tracks via the pylast library, all through the comfort of a web interface powered by Flask.

## Why?

For scrobbling, I use `yams` with `ncmpcpp` as well as Plex's last.fm integration, but I didn't have a way to scrobble all the vinyl/tapes I listen to. So, I worked with ChatGPT on a simple scrobbler and figured others may find some benefit in it as well! The web interface came later, and I decided it would make more sense to split this into a separate project. Perhaps they will be combined at some point in the future.

## API Setup

Create an API key here: https://www.last.fm/api/account/create

Stick the API key in a file `~/.config/pylast/api_key` and the shared secret into `~/.config/pylast/api_secret` -- there should be nothing else in these files, just the key, with no new line

For reference, you can find previous keys/secrets you've created here: https://www.last.fm/api/accounts

## Usage 

`python web_scrobbler.py`

## Dependencies

### pylast

On Arch Linux with `yay`, I install via `yay pylast`

But the install directions are also available:

* https://pypi.org/project/pylast/
* https://github.com/pylast/pylast#installation

### Flask

On Arch Linux with `yay`, I install via `yay python-flask`

But the install directions are also available:
* https://pypi.org/project/Flask/
* https://github.com/pallets/flask#installing