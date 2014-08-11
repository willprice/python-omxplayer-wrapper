# DBus functions to wrap:
## MPRIS interface:
- `CanQuit` :: boolean
- `Fullscreen` :: boolean
- `CanSetFullscreen` :: boolean
- `CanRaise` :: boolean
- `HasTrackList` :: boolean
- `Identity` :: string
- `SupportedUriSchemes` :: string[]
- `SupportedMimeTypes` :: string[] (_NOT IMPLEMENT IN OMXPLAYER_)
- `CanGoNext` :: boolean
- `CanGoPrevious` :: boolean
- `CanSeek` :: boolean
- `CanControl` :: boolean
- `CanPlay` :: boolean
- `CanPause` :: boolean
- `PlaybackStatus` :: string : ['Paused', 'Playing']
- `Volume [(volume :: double)]` :: double
- `Mute` :: null
- `Unmute` :: null
- `Position` :: int64
- `Duration` :: int64
- `MinimumRate` :: double
- `MaximumRate` :: double

## Player interface:
- `Next` :: null
- `Previous` :: null
- `PlayPause` :: null
- `Pause` :: null (same as above)
- `Stop` :: null
- `Seek(offest_in_microseconds :: int64)` :: null | int64 (null if offset is invalid)
- `SetPosition(path :: string, position_in_microseconds :: int64)` :: null | int64 (null if position is invalid)
- `ListSubtitles` :: string[] each item of the form: `<index>:<lang>:<name>:<codec>:<active>`
- `ListAudio` :: string[], each item of the form: `<index>:<lang>:<name>:<codec>:<active>`
- `ListVideo` :: string[], each item of the form: `<index>:<lang>:<name>:<codec>:<active>`
- `SelectSubtitle(index_of_subtitle :: int32)` :: boolean
- `SelectAudio(index_of_audio_stream :: int32)` :: boolean
- `ShowSubtitles` :: null (turns subtitles on)
- `HideSubtitles` :: null (turns subtitles off)
- `Action(command :: int32)` :: null

## Root interface:
- `Quit` :: null
