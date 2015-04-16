#!/usr/bin/env python2
from omxplayer import OMXPlayer
from time import sleep

vid = OMXPlayer('../chocolate-adventure/media/temple.mkv')
print("Start playing")
vid.play()
sleep(2)

print("Stop playing")
vid.pause()
sleep(2)

print("Exit")
vid.quit()
