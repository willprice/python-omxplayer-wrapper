#!/usr/bin/env python2
import os.path
from time import sleep
from omxplayer import OMXPlayer
from smoke_tests import TEST_MEDIA_FILE_1, TEST_MEDIA_FILE_2

vid1 = OMXPlayer(TEST_MEDIA_FILE_1)
print("Start playing vid1")
sleep(5)

print("Stop playing vid1")
vid1.pause()
sleep(2)

print("Exit vid1")
vid1.quit()
sleep(1)


vid2 = OMXPlayer(TEST_MEDIA_FILE_2)
print("Start playing vid2")
sleep(2)

print("Stop playing vid2")
vid2.pause()
sleep(2)

print("Exit vid2")
vid2.quit()
