#!/usr/bin/env python2
from omxplayer import OMXPlayer
from time import sleep
from . import TEST_MEDIA_FILE_1


vid1 = OMXPlayer(TEST_MEDIA_FILE_1)
print("Start playing")
vid1.play()
sleep(2)
print("Stop playing")
vid1.pause()
sleep(2)
print("Exit")
vid1.exit()
