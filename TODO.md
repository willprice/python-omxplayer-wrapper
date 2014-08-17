To pass the _basic playback_ user story we must implement the following functions defined in the DBus spec:

- `Pause`
- `Position`
- `CanQuit`
- `Quit`

To implement these functions we'll need to:
1. Open up a specific file (which initiates playback)
2. Check `Position` until we're at 1 second of playback
3. Use `Pause` to pause playback
4. Check that OMXPlayer `CanQuit` and then if so `Quit`, else throw an exception.
