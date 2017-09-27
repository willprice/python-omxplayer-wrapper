#!/usr/bin/env python

from time import sleep
import os
import dbus

import unittest

from omxplayer import OMXPlayer, keys

# Decimal places for numerical comparison
_TIME_DP=0
_RATE_DP=2
_VOLUME_DP=3


class OMXPlayerTest(unittest.TestCase):
    MEDIA_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../media/test_media_1.mp4')

    def setUp(self):
        self.player = OMXPlayer(self.MEDIA_FILE_PATH)
        sleep(1) # Give the player time to start up

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
        self.player.pause()
        self.assertEqual("Paused", self.player.playback_status())

    def test_volume(self):
        self.assertEqual(0.0, self.player.volume(), _VOLUME_DP)

    def test_set_volume(self):
        self.assertAlmostEqual(0.0, self.player.volume(), _VOLUME_DP)
        self.player.set_volume(1)
        self.assertAlmostEqual(1.0, self.player.volume(), _VOLUME_DP)

    def test_position(self):
        self.assertTrue(self.player.position() < 1.0)

    def test_minimum_rate(self):
        self.assertAlmostEqual(0.001, self.player.minimum_rate(), _RATE_DP)

    def test_maximum_rate(self):
        self.assertAlmostEqual(4.0, self.player.maximum_rate(), _RATE_DP)

    def test_rate(self):
        self.assertAlmostEqual(1.0, self.player.rate(), _RATE_DP)

    def test_set_rate(self):
        self.assertAlmostEqual(1.0, self.player.rate(), _RATE_DP)
        new_rate = 0.5

        self.player.set_rate(new_rate)
        sleep(0.2)

        self.assertAlmostEqual(new_rate, self.player.rate(), _RATE_DP)

    def test_metadata(self):
        expectedMetadata = {
            'mpris:length': 19691000,
            'xesam:url': 'file://' + os.path.abspath(self.MEDIA_FILE_PATH)
        }
        self.assertEqual(expectedMetadata, self.player.metadata())


class OMXPlayerPlayerNonStandardPropertiesTest(OMXPlayerTest):
    def test_aspect(self):
        self.assertEqual(0, self.player.aspect_ratio())

    def test_video_stream_count(self):
        self.assertEqual(1, self.player.video_stream_count())

    def test_video_width(self):
        self.assertEqual(1280, self.player.width())

    def test_video_height(self):
        self.assertEqual(720, self.player.height())

    def test_duration(self):
        self.assertAlmostEqual(19.691, self.player.duration(), _TIME_DP)


class OMXPlayerPlayerInterfaceMethodsTest(OMXPlayerTest):
    def test_get_source(self):
        self.assertEqual(self.MEDIA_FILE_PATH, self.player.get_source())

    def test_next(self):
        self.player.next()

    def test_previous(self):
        self.player.previous()

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
        self.player.seek(10)
        self.assertAlmostEqual(initial_position + 10, self.player.position(), _TIME_DP)

    def test_set_position(self):
        self.player.set_position(10)
        self.assertAlmostEqual(10, self.player.position(), _TIME_DP)

    def test_set_alpha(self):
        self.player.set_alpha(255)

    def test_set_aspect_mode(self):
        self.player.set_aspect_mode("stretch")

    def test_mute(self):
        self.player.set_volume(1)

        self.player.mute()

        self.assertAlmostEqual(0, self.player.volume(), _VOLUME_DP)

    def test_unmute(self):
        self.player.set_volume(1)
        self.player.mute()
        self.assertAlmostEqual(0, self.player.volume(), _VOLUME_DP)

        self.player.unmute()
        self.assertAlmostEqual(1, self.player.volume(), _VOLUME_DP)

    def test_list_subtitles(self):
        self.assertEqual([], self.player.list_subtitles())

    def test_set_video_crop(self):
        self.player.set_video_crop(0, 0, 100, 100)

    def test_hide_video(self):
        self.player.hide_video()

    def test_show_video(self):
        self.player.show_video()

    def test_list_audio(self):
        self.assertEqual(1, len(self.player.list_audio()))

    def test_list_video(self):
        self.assertEqual(1, len(self.player.list_video()))

    def test_select_subtitle(self):
        self.player.select_subtitle(0)

    def test_select_audio(self):
        self.player.select_audio(0)

    def test_show_subtitles(self):
        self.player.show_subtitles()

    def test_hide_subtitles(self):
        self.player.hide_subtitles()

    def test_action(self):
        self.player.action(keys.SHOW_INFO)

class OMXPlayerPlayerInterfaceNonStandardMethodsTest(OMXPlayerTest):
    pass
