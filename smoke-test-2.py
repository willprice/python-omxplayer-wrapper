#!/usr/bin/env python2
from omxplayer import OMXPlayer
from time import sleep

vid1 = OMXPlayer('../chocolate-adventure/media/temple.mkv')
print("Start playing vid1")
vid1.play()
sleep(2)
print("Stop playing vid1")
vid1.pause()
sleep(2)
print("Exit vid1")
vid1.quit()
sleep(1)

vid2 = OMXPlayer('../chocolate-adventure/media/escape_scene.mkv')
print("Start playing vid2")
vid2.play()
sleep(2)
print("Stop playing vid2")
vid2.pause()
sleep(2)
print("Exit vid2")
vid2.quit()
