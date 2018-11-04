# 0.3.0 -> 0.3.1
* Remove `tests` package from distribution
* Support calling `quit` multiple times without raising exception

# 0.2.5 -> 0.3.0

* Change `set_volume` to work with values between 0-10 instead of
  millibels
* Fix `volume` to return actual volume rather than just 1.0
* Fix `rate` to return actual rate rather than just 1.0
* Support providing arguments as a `str` which is then split with `shlex.split`,
  i.e. you don't have to provide a list of shell split args if you don't want to.
* Support `str` media file path in `OMXPlayer` constructor.
* Cleanup omxplayer process on exit


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
