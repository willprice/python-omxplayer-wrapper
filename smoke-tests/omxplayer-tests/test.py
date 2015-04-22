#!/usr/bin/env python2
from omxplayer import OMXPlayer
from time import sleep

vid1 = OMXPlayer('~/chocolate-adventure/media/temple.mkv')
print("Start playing")
vid1.play()
sleep(2)
print("Stop playing")
vid1.pause()
sleep(2)
print("Exit")
vid1.exit()
