# Acceptance fixtures: video clipping

`../acceptance.py` (issue #124) has no fixture files of its own. On each
run it builds the clipper's SYNTHETIC fixture with
`make_fixture()` from `../../tests/test_clipper.py`, which is committed
code:
- a 60 second test pattern video with tones;
- a synthetic word timing transcript about home batteries.

No third party media and no real person are used. The fixture has no
retention or "most replayed" data, because the clipper has no input for
it (see the acceptance output, criterion 3).
