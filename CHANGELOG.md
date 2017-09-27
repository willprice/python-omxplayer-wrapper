# 0.2.4 -> 0.2.5

* Correct `omxplayer.__version__` to return 0.2.5 instead of 0.2.3 (in 0.2.4)

# 0.2.3 -> 0.2.4

* New methods:
  * `aspect_ratio`
  * `can_raise`
  * `fullscreen`
  * `has_track_list`
  * `height`
  * `hide_subtitles`
  * `hide_video`
  * `metadata`
  * `next`
  * `previous`
  * `rate`
  * `select_audio`
  * `select_subtitle`
  * `set_rate`
  * `show_subtitles`
  * `show_video`
  * `supported_uri_schemes`
  * `video_pos`
  * `video_stream_count`
  * `width`
* We no longer verify the source exists before playing to allow a broader range
  of valid inputs
* Revamped docs, available at http://python-omxplayer-wrapper.readthedocs.io/
 
## Developer relevant changes

* Added integration tests
* Refactored tests
* Unit testing on python 3.5 and 3.6 in travis
