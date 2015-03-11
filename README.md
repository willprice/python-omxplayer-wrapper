
# Python OMXPlayer wrapper

> Control OMXPlayer from Python on the Raspberry Pi.

A completely rewritten version of PyOMXPlayer utilising `OMXPlayer`'s `DBus` interface.

## Hello world
WARNING: Don't have an RPi to test this at the moment, please report an issue if this doesn't work!

```python
from omxplayer import OMXPlayer
from time import sleep

# This will start an `omxplayer` process, this might 
# fail the first time you run it, currently in the 
# process of fixing this though.
player = OMXPlayer('path/to/file.mp4')

# The player will initially be paused

player.play()
sleep(5)
player.pause()

# Kill the `omxplayer` process gracefully.
player.quit()
```
