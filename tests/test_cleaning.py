"""Deterministic unit tests for the pure cleaning helpers in build_database.py."""

import math

import pytest

import build_database as bd


class TestCleanYears:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("Less than 1 year", 0.5),
            ("More than 50 years", 55),
            ("10", 10.0),
            ("5.5", 5.5),
            (10, 10.0),
            (0, 0.0),
        ],
    )
    def test_known_values(self, raw, expected):
        assert bd.clean_years(raw) == expected

    @pytest.mark.parametrize("raw", [None, math.nan, float("nan")])
    def test_nan_returns_none(self, raw):
        assert bd.clean_years(raw) is None

    @pytest.mark.parametrize("raw", ["", "   ", "not a number", "1-2 years", "N/A"])
    def test_unparseable_returns_none(self, raw):
        assert bd.clean_years(raw) is None

    def test_whitespace_is_stripped(self):
        assert bd.clean_years("  Less than 1 year  ") == 0.5


class TestSplitMulti:
    def test_deduplicates_preserving_order(self):
        assert bd.split_multi("Python;Python") == ["Python"]
        assert bd.split_multi("Python;SQL;Python") == ["Python", "SQL"]
        assert bd.split_multi("A; B ;A;C") == ["A", "B", "C"]

    def test_strips_and_drops_empties(self):
        assert bd.split_multi("A;;B;  ;C") == ["A", "B", "C"]

    @pytest.mark.parametrize("raw", [None, math.nan, "", "   "])
    def test_empty_input(self, raw):
        assert bd.split_multi(raw) == []


class TestMappings:
    def test_likert_map_is_complete_and_ordinal(self):
        assert bd.LIKERT_MAP == {
            "Strongly disagree": 1,
            "Disagree": 2,
            "Neither agree nor disagree": 3,
            "Agree": 4,
            "Strongly agree": 5,
        }

    def test_years_sentinels(self):
        assert bd.YEARS_CODE_MAP["Less than 1 year"] == 0.5
        assert bd.YEARS_CODE_MAP["More than 50 years"] == 55

    def test_age_prefer_not_to_say_maps_to_none(self):
        assert bd.AGE_MAP["Prefer not to say"] is None

    def test_aspect_map_has_nine_aspects(self):
        assert len(bd.ASPECT_MAP) == 9
        assert len(set(bd.ASPECT_MAP.values())) == 9

    def test_eleven_tech_categories(self):
        assert len(bd.TECH_CATEGORIES) == 11
        assert len(bd.VARIANTS) == 3
        assert bd.TECH_CATEGORIES == [
            "Language",
            "Database",
            "Platform",
            "Webframe",
            "Embedded",
            "MiscTech",
            "ToolsTech",
            "NEWCollabTools",
            "OfficeStackAsync",
            "OfficeStackSync",
            "AISearchDev",
        ]
