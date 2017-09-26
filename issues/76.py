#!/usr/bin/env python2
from omxplayer.player import OMXPlayer
import os
from time import sleep

DEBUG = 1

def debug(*args):
    if (DEBUG):
        text = " ".join(list(map(str, args)))
        print text

def play_film(filename="demo.mp4", duration=0, position=0):
    debug("\nfilename:", filename)
    debug("  position:", position)
    debug("  duration:", duration)
    trim_from_end = 0.5
    #trim_from_end = 0
    player = OMXPlayer(filename)
    player.set_position(0.0)
    debug("  pre-play pos:", player.position())
    player.play()
    # check and set position
    full_length = player.duration()
    # if the position is imposible, set it to 0
    if position <= 0 or position > full_length:
        position = 0.0
    player.set_position(position)
    # check and set duration
    length_to_end = player.duration()
    # if duration is imposible, set it to the length_to_end
    if duration == 0 or duration > length_to_end:
        wait = length_to_end - trim_from_end
    else:
        wait = duration
    if wait < 0:
        wait = 0
    debug("  full length: ", full_length)
    debug("  length to end: ", length_to_end)
    debug("  wait: ", wait)
    sleep(wait)
    debug("  post sleep pos:", player.position())
    player.pause()
    player.quit()
    debug("  post pause pos:", player.position())
    return True

def main():
    src = "../tests/media/test_media_1.mp4"
    assert os.path.exists(src)
    play_film(src, position=5, duration=5)


main()
