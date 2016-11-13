#!/usr/bin/env python2
from omxplayer import OMXPlayer
from time import sleep
from smoke_tests import TEST_MEDIA_FILE_1


print(TEST_MEDIA_FILE_1)
vid1 = OMXPlayer(TEST_MEDIA_FILE_1, pause=True)
print("Start playing")
vid1.set_position(5)
vid1.play()
sleep(2)
print("Stop playing")
vid1.pause()
sleep(2)
print("Exit")
vid1.quit()
