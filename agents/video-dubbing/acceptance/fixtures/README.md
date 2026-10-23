# Acceptance fixtures: video dubbing

`../acceptance.py` (issue #124) has no fixture files of its own. On each
run it builds the dubber's SYNTHETIC fixture from committed code in
`../../tests/test_dubber.py`:
- a test pattern video;
- two speakers synthesized with ffmpeg's flite stock voices, so no real
  person;
- a generated two tone music bed;
- the suite's four timed segments and its es and fr glossary.

The own-voice case writes a SYNTHETIC consent record into a temporary
folder. It names no real person.
