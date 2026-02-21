from datetime import datetime

from glosa_extractor.normalization import normalize_date, parse_decimal


def test_normalize_date_from_iso_to_dd_mm_yyyy():
    assert normalize_date("2026-02-21") == "21-02-2026"


def test_normalize_date_from_datetime_to_dd_mm_yyyy():
    assert normalize_date(datetime(2026, 2, 21)) == "21-02-2026"


def test_parse_decimal_handles_dot_as_decimal_separator():
    assert parse_decimal("103.5") == 103.5


def test_parse_decimal_handles_comma_as_decimal_separator():
    assert parse_decimal("103,5") == 103.5


def test_parse_decimal_handles_br_thousands_and_decimal():
    assert parse_decimal("1.234,56") == 1234.56
