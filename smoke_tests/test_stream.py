#!/usr/bin/env python2
from omxplayer import OMXPlayer
from time import sleep
from smoke_tests import TEST_STREAM_FILE_1

print("Streaming " + TEST_STREAM_FILE_1)
print("Starting OMXPlayer")
vid1 = OMXPlayer(TEST_STREAM_FILE_1)
for i in range(0, 10):
    print("sleeping %s" % i)
    sleep(1)
print("Pause for 2 seconds")
vid1.pause()
sleep(2)
print("Exiting")
vid1.quit()
