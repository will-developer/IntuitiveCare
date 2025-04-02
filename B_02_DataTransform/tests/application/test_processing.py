import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from typing import List, Dict, Any

from src.application.processing import process_extracted_tables

@pytest.fixture
def sample_tables_ok() -> List[pd.DataFrame]:
    return [
        pd.DataFrame({'A': ['1', '2'], 'B': ['3', '4'], 'OD': ['Y', 'N']}),
        pd.DataFrame({'A': ['5', '6'], 'B': ['7', '8'], 'AMB': ['X', 'Y']}),
        pd.DataFrame({'C': [None, None], 'D': [None, None]}),
        pd.DataFrame({'A': ['9'], 'OD': ['Y']}),
    ]

@pytest.fixture
def sample_rename_map() -> Dict[str, str]:
    return {'OD': 'Dental Insurance', 'AMB': 'Ambulatorial Insurance', 'NonExistent': 'WontAppear'}

def test_process_extracted_tables_success(sample_tables_ok: List[pd.DataFrame], sample_rename_map: Dict[str, str]):
    result = process_extracted_tables(sample_tables_ok, sample_rename_map)

    expected_data = {
        'A': ['1', '2', '5', '6', '9'],
        'B': ['3', '4', '7', '8', None],
        'Dental Insurance': ['Y', 'N', None, None, 'Y'],
        'Ambulatorial Insurance': [None, None, 'X', 'Y', None]
    }
    expected_df = pd.DataFrame(expected_data).astype(str).replace('nan', 'None')
    result_str = result.astype(str).replace('nan', 'None')

    assert result is not None
    assert_frame_equal(result_str.sort_index(axis=1), expected_df.sort_index(axis=1), check_dtype=False)
    assert 'Dental Insurance' in result.columns
    assert 'Ambulatorial Insurance' in result.columns
    assert 'OD' not in result.columns
    assert 'AMB' not in result.columns
    assert 'NonExistent' not in result.columns

def test_process_extracted_tables_empty_input():
    result = process_extracted_tables([], {'OD': 'Dental'})
    assert result is None

def test_process_extracted_tables_all_empty_after_clean():
    tables = [
        pd.DataFrame({'A': [None, None], 'B': [None, None]}),
        pd.DataFrame(),
    ]
    result = process_extracted_tables(tables, {'A': 'ColA'})
    assert result is None

def test_process_extracted_tables_with_none_and_invalid_types():
    tables: List[Any] = [
        pd.DataFrame({'A': ['1'], 'OD': ['Y']}),
        None,
        pd.DataFrame({'B': ['2'], 'AMB': ['N']}),
        "not a dataframe",
        pd.DataFrame({'A': ['3']}),
    ]
    result = process_extracted_tables(tables, {'OD': 'Dental', 'AMB': 'Ambulance'})

    expected_data = {
        'A': ['1', None, '3'],
        'Dental': ['Y', None, None],
        'B': [None, '2', None],
        'Ambulance': [None, 'N', None]
    }
    expected_df = pd.DataFrame(expected_data).astype(str).replace('nan', 'None')
    result_str = result.astype(str).replace('nan', 'None')

    assert result is not None
    assert_frame_equal(result_str.sort_index(axis=1), expected_df.sort_index(axis=1), check_dtype=False)

def test_process_extracted_tables_no_rename_map():
    tables = [pd.DataFrame({'A': ['1'], 'OD': ['Y']})]
    result = process_extracted_tables(tables, {})

    expected_df = pd.DataFrame({'A': ['1'], 'OD': ['Y']})

    assert result is not None
    assert_frame_equal(result, expected_df)

def test_process_extracted_tables_rename_map_no_match():
    tables = [pd.DataFrame({'A': ['1'], 'B': ['Y']})]
    result = process_extracted_tables(tables, {'C': 'ColC', 'D': 'ColD'})

    expected_df = pd.DataFrame({'A': ['1'], 'B': ['Y']})

    assert result is not None
    assert_frame_equal(result, expected_df)