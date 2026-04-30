import pytest
from app import app, generate_voter_id
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test if home page loads successfully"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'VoteGuide AI' in rv.data

def test_guide_route(client):
    """Test if the guide returns all steps"""
    rv = client.get('/guide')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'steps' in json_data
    assert len(json_data['steps']) > 0

def test_ask_empty(client):
    """Test edge case: Empty query to AI"""
    rv = client.get('/ask')
    assert rv.status_code == 200
    assert rv.get_json()['message'] == 'Please ask a question.'

def test_ask_query(client):
    """Test normal query to AI"""
    rv = client.get('/ask?q=how')
    assert rv.status_code == 200
    assert 'message' in rv.get_json()

def test_check_eligibility_valid(client):
    """Test valid age eligibility"""
    rv = client.get('/check?age=20')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['eligible'] is True
    assert 'eligible' in json_data['result']

def test_check_eligibility_invalid_age(client):
    """Test invalid age eligibility"""
    rv = client.get('/check?age=16')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['eligible'] is False
    assert 'must be 18' in json_data['result']

def test_check_eligibility_missing_age(client):
    """Test edge case: Missing age parameter"""
    rv = client.get('/check')
    assert rv.status_code == 200
    assert rv.get_json()['eligible'] is False

def test_generate_voter_id_success(client):
    """Test full integration flow: successful voter ID generation"""
    rv = client.post('/generate', json={
        "name": "Test User",
        "age": "25",
        "address": "123 Tech Park"
    })
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['success'] is True
    assert 'Test User' in json_data['message']

def test_generate_voter_id_missing_fields(client):
    """Test edge cases: missing fields in registration"""
    rv = client.post('/generate', json={
        "name": "",
        "age": "16",
        "address": ""
    })
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['success'] is False
    assert 'Name is missing' in json_data['message']
    assert 'Address is missing' in json_data['message']
    assert 'Age must be 18+' in json_data['message']

def test_generate_voter_id_invalid_age_format(client):
    """Test edge case: invalid age format"""
    rv = client.post('/generate', json={
        "name": "Test",
        "age": "abc",
        "address": "Test Addr"
    })
    assert rv.status_code == 200
    assert rv.get_json()['success'] is False
    assert 'Valid age is required' in rv.get_json()['message']
