#!/usr/bin/env python2
import os.path
from time import sleep
from omxplayer import OMXPlayer
from smoke_tests import TEST_MEDIA_FILE_1, TEST_MEDIA_FILE_2

player = OMXPlayer(TEST_MEDIA_FILE_1, pause=True)
print("Start playing vid1")
player.play()
sleep(2)
print("Stop playing vid1")
player.pause()
sleep(2)


player.load(TEST_MEDIA_FILE_2, pause=True)
print("Start playing vid2")
player.play()
sleep(2)
print("Stop playing vid2")
player.pause()
sleep(2)

print("Exit")
player.quit()
sleep(1)
