import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from app import calculate_score, CATEGORIES_ALL_OPTION, filter_data

# Mock data for testing
element = {
    'kategoria': 'Sport',
    'wspolrzedne': [52.2297, 21.0122],  # Coordinates for Warsaw
    'data_od': '2024-02-01',
    'data_do': '2024-02-10',
    'preferencje_kandydata': ['Football', 'Running']
}

def test_category_mismatch():
    assert calculate_score(element, 10, (52.2297, 21.0122), date(2024, 2, 1), date(2024, 2, 10), 'Music', ['Football']) == (.0, set())

def test_distance_greater_than_given():
    assert calculate_score(element, 1, (53.2297, 21.0122), date(2024, 2, 1), date(2024, 2, 10), 'Sport', ['Football']) == (.0, set())

def test_date_range_mismatch():
    assert calculate_score(element, 10, (52.2297, 21.0122), date(2024, 3, 1), date(2024, 3, 10), 'Sport', ['Football']) == (.0, set())

def test_preferences_calculation():
    score, intersection = calculate_score(element, 10, (52.2297, 21.0122), date(2024, 2, 1), date(2024, 2, 10), 'Sport', ['Football', 'Basketball'])
    assert score == 0.5 and intersection == {'Football'}

def test_no_preferences():
    assert calculate_score(element, 10, (52.2297, 21.0122), date(2024, 2, 1), date(2024, 2, 10), 'Sport', None) == (1.0, set())

def test_valid_scenario():
    score, intersection = calculate_score(element, 10, (52.2297, 21.0122), date(2024, 2, 1), date(2024, 2, 10), CATEGORIES_ALL_OPTION, ['Football', 'Basketball'])
    assert score == 0.5 and intersection == {'Football'}

