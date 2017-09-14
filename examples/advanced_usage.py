#!/usr/bin/env python3

from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep

VIDEO_1_PATH = Path("../tests/media/test_media_1.mp4")
VIDEO_2_PATH = Path("../tests/media/test_media_2.mp4")

player = OMXPlayer(VIDEO_1_PATH)
player.play()

sleep(5)

player.load(VIDEO_2_PATH)

sleep(5)

player.pause()

player2 = OMXPlayer(VIDEO_2_PATH, dbus_name='org.mpris.MediaPlayer2.omxplayer1', pause=True)
player2.set_transparency(255/2)
player2.play()

sleep(10)

player.quit()
player2.quit()
