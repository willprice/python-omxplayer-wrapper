#!/usr/bin/env python2

from omxplayer.player import OMXPlayer
import time
import logging
import logging.config
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


def playMedia(path="../tests/media/test_media_1.mp4", duration=0, position=0):
    player = OMXPlayer(path, args=["--no-osd"])
    player.set_aspect_mode("fill")
    if position > 0:
            player.set_position(position)
    #player.duration() # this only works if this line is here
    if duration == 0:
            duration = player.duration() - position
    player.play()
    time.sleep(duration)
    player.quit()

log.info("Start playMedia")
playMedia(duration=6)
log.info("playMedia call complete")
