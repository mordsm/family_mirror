from src.utils.timecodes import format_timecode, overlap_seconds


def test_format_timecode_without_hours():
    assert format_timecode(65.4321) == "01:05.432"


def test_format_timecode_with_hours():
    assert format_timecode(3661.2) == "01:01:01.200"


def test_overlap_seconds():
    assert overlap_seconds(1.0, 4.0, 3.0, 5.0) == 1.0
    assert overlap_seconds(1.0, 2.0, 3.0, 4.0) == 0.0
