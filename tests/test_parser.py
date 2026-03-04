import pytest
import tempfile
import yaml
from apexhunter.parser import PlaybookParser

def test_valid_playbook():
    valid_yaml = {
        'name': 'Test Playbook',
        'hypothesis': 'Testing the parser',
        'steps': [{'id': 'step1', 'description': 'test', 'query': 'SELECT * FROM test'}]
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(valid_yaml, f)
        filepath = f.name
    
    parser = PlaybookParser(filepath)
    parsed = parser.parse()
    assert parsed['name'] == 'Test Playbook'
    assert len(parsed['steps']) == 1

def test_invalid_playbook_missing_name():
    invalid_yaml = {
        'hypothesis': 'Missing name',
        'steps': [{'id': 'step1', 'description': 'test', 'query': 'SELECT * FROM test'}]
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(invalid_yaml, f)
        filepath = f.name
    
    parser = PlaybookParser(filepath)
    with pytest.raises(ValueError, match="Playbook missing required top-level field: 'name'"):
        parser.parse()
