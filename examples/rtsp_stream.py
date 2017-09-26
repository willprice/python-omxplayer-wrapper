#!/usr/bin/env python3

from omxplayer.player import OMXPlayer
from time import sleep

STREAM_URI = 'rtsp://184.72.239.149/vod/mp4:BigBuckBunny_175k.mov'

player = OMXPlayer(STREAM_URI)
player.play()

sleep(5)

player.quit()
