# Python OMXPlayer wrapper

[![PyPI Version](https://img.shields.io/pypi/v/omxplayer-wrapper.svg?maxAge=2592000)](https://pypi.python.org/pypi/omxplayer-wrapper)
[![PyPI Python versions](https://img.shields.io/pypi/pyversions/omxplayer-wrapper.svg)](https://pypi.python.org/pypi/omxplayer-wrapper)
[![PyPI License](https://img.shields.io/pypi/l/omxplayer-wrapper.svg?maxAge=2592000)](https://pypi.python.org/pypi/omxplayer-wrapper)
[![Documentation
Status](https://readthedocs.org/projects/python-omxplayer-wrapper/badge/?version=latest)](https://readthedocs.org/projects/python-omxplayer-wrapper/?badge=latest)
[![Build Status](https://travis-ci.org/willprice/python-omxplayer-wrapper.svg?branch=develop)](https://travis-ci.org/willprice/python-omxplayer-wrapper)
[![Code Coverage](https://codecov.io/gh/willprice/python-omxplayer-wrapper/branch/develop/graph/badge.svg)](https://codecov.io/gh/willprice/python-omxplayer-wrapper)


> Control OMXPlayer from Python on the Raspberry Pi.

## Install
Make sure dbus is installed:
```shell
$ sudo apt-get install python-dbus
```

For someone who just wants to use the package:
```shell
$ python setup.py install
```

If you're feeling helpful, and decide to help develop the package:
```shell
$ python setup.py develop
```
There's also an Ansible playbook in `devenv` which will set up a raspberry pi
with omxplayer-wrapper in develop mode (located at
`/usr/src/omxplayer-wrapper`) which can be used by running `./devenv/deploy.sh`

This will install via symlinks so that you can continue to work on it locally
but import it from other python packages

## Hello world
```python
from omxplayer import OMXPlayer
from time import sleep

file_path_or_url = 'path/to/file.mp4'

# This will start an `omxplayer` process, this might
# fail the first time you run it, currently in the
# process of fixing this though.
player = OMXPlayer(file_path_or_url)

# The player will initially be paused

player.play()
sleep(5)
player.pause()

# Kill the `omxplayer` process gracefully.
player.quit()
```

Playing a stream from a URL (e.g. a live RTMP or RTSP stream) works the same as with a file path, just change the "source" string parameter given to `OMXPlayer` to a URL instead of a file path.
```python
from omxplayer import OMXPlayer
from time import sleep

file_path_or_url = 'rtmp://192.168.0.1/live/test'

player = OMXPlayer(file_path_or_url)

# The player will initially be paused

player.play()
sleep(5)
player.pause()

# Kill the `omxplayer` process gracefully.
player.quit()
```

## Usage patterns
*Choppy streaming over a slow connection?* If you're connection isn't good
enough to support streaming, checkout `urllib2` to download the file locally
prior to playing.


## Docs
You can read the docs here:
[python-omxplayer-wrapper.rtfd.org](http://python-omxplayer-wrapper.rtfd.org)
