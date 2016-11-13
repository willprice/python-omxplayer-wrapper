# -*- coding: utf-8 -*-
import os.path
import logging

logging.basicConfig(level=logging.DEBUG)


_file_path = os.path.realpath(__file__)
_media_path = os.path.dirname(_file_path) + "/media"

TEST_MEDIA_FILE_1  = _media_path + "/test_media_1.mp4"
TEST_MEDIA_FILE_2  = _media_path + "/test_media_2.mp4"
TEST_STREAM_FILE_1 = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"
