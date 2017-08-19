# Smoke Tests

These are tests (also function very well as example usage) to test out the behaviour
of the wrapper. They are executed and verified manually[1].

## Tests

* **Basic**, run a video from start to finish, tests the lifecycle of the
  `OMXPlayer` object ensuring it can construct and manage the dbus session for
   duration of a single video
* **Multiple Videos**, run two videos consecutively using
  * Two `OMXPlayer` objects
  * One `OMXPlayer` instance and `load`
* **Multiple Videos** concurrently split screen
* **Remote stream**
  * Single video
  * Multiple videos

[1]: Unless anyone else has a better idea for integration tests for verifying
     the correctness of the library?
