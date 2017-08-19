#!/usr/bin/env python

from time import sleep
import os
import dbus

import unittest

from omxplayer import OMXPlayer


class OMXPlayerTest(unittest.TestCase):
    MEDIA_FILE_PATH = './media/test_media_1.mp4'

    def setUp(self):
        self.player = OMXPlayer(self.MEDIA_FILE_PATH)

    def tearDown(self):
        self.player.quit()


class OMXPlayerRootInterfacePropertiesTest(OMXPlayerTest):
    def test_can_quit(self):
        self.assertTrue(self.player.can_quit())

    def test_fullscreen(self):
        self.assertTrue(self.player.fullscreen())

    def test_can_set_fullscreen(self):
        self.assertFalse(self.player.can_set_fullscreen()) # can't set fullscreen because on start it already is

    def test_can_raise(self):
        self.assertFalse(self.player.can_raise())

    def test_has_track_list(self):
        self.assertFalse(self.player.has_track_list())

    def test_identity(self):
        self.assertEqual("OMXPlayer", self.player.identity())

    def test_supported_uri_schemes(self):
        self.assertEqual(["file", "http", "rtsp", "rtmp"], self.player.supported_uri_schemes())


class OMXPlayerPlayerInterfacePropertiesTest(OMXPlayerTest):
    def test_can_go_next(self):
        self.assertFalse(self.player.can_go_next())

    def test_can_go_previous(self):
        self.assertFalse(self.player.can_go_previous())

    def test_can_seek(self):
        self.assertTrue(self.player.can_seek())

    def test_can_control(self):
        self.assertTrue(self.player.can_control())

    def test_can_play(self):
        self.assertTrue(self.player.can_play())

    def test_can_pause(self):
        self.assertTrue(self.player.can_pause())

    def test_playback_status(self):
        self.assertEqual("Paused", self.player.playback_status())

    def test_volume(self):
        self.assertEqual(0.0, self.player.volume())

    def test_position(self):
        self.assertTrue(self.player.position() < 1.0)

    def test_minimum_rate(self):
        self.assertEqual(0, self.player.minimum_rate())

    def test_maximum_rate(self):
        self.assertEqual(10.125, self.player.maximum_rate())

    def test_rate(self):
        self.assertEqual(4.0, self.player.rate())

    def test_metadata(self):
        expectedMetadata = {
            'mpris:length': 19691000,
            'xesam:url': 'file://' + os.path.abspath(self.MEDIA_FILE_PATH)
        }
        self.assertEqual(expectedMetadata, self.player.metadata())

    def test_aspect(self):
        self.assertEqual(0, self.player.aspect_ratio())

    def test_video_stream_count(self):
        self.assertEqual(1, self.player.video_stream_count())

    def test_video_width(self):
        self.assertEqual(1280, self.player.width())

    def test_video_height(self):
        self.assertEqual(720, self.player.height())

    def test_duration(self):
        self.assertEqual(19.691, self.player.duration(), 0.00001)


class OMXPlayerPlayerInterfaceMethodsTest(OMXPlayerTest):
    def test_playing_on_start(self):
        sleep(1) # it takes a while for omxplayer to load and start playing
                 # before starting video playback on startup it will be in the
                 # "Paused" state
        self.assertEqual("Playing", self.player.playback_status())

    def test_play_pause(self):
        self.player.play_pause()
        self.assertEqual("Paused", self.player.playback_status())

        self.player.play_pause()
        self.assertEqual("Playing", self.player.playback_status())

    def test_pause(self):
        self.player.pause()
        self.assertEqual("Paused", self.player.playback_status())

    def test_stop(self):
        self.player.stop()
        self.assertRaises(dbus.DBusException, self.player.playback_status)

    def test_seek(self):
        initial_position = self.player.position()
        self.player.seek(1000)
        self.assertEqual(initial_position + 1000, self.player.position() / 1000, 10)

    def test_set_position(self):
        self.player.set_position(1000)
        self.assertEqual(1000 , self.player.position() / 1000, 10)

    def test_mute(self):
        self.player.set_volume(1)
        self.player.mute()
        self.assertEqual(0, self.player.volume())

    def test_unmute(self):
        self.player.set_volume(1)
        self.player.mute()
        self.player.unmute()
        self.assertEqual(1, self.player.volume())
