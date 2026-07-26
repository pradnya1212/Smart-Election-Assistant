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
    assert '18 or older' in json_data['result']

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

def test_multilang_guide(client):
    """Test localized guide steps for Hindi and Marathi"""
    rv_hi = client.get('/guide?lang=Hindi')
    assert rv_hi.status_code == 200
    assert 'पात्रता जांचें' in rv_hi.get_json()['steps'][0]

    rv_mr = client.get('/guide?lang=Marathi')
    assert rv_mr.status_code == 200
    assert 'पात्रता तपासा' in rv_mr.get_json()['steps'][0]

def test_multilang_check(client):
    """Test localized eligibility response"""
    rv = client.get('/check?age=20&lang=Hindi')
    assert rv.status_code == 200
    assert 'पात्र' in rv.get_json()['result']

def test_multilang_generate(client):
    """Test localized voter ID advice tag"""
    rv = client.post('/generate', json={
        "name": "राहुल",
        "age": "22",
        "address": "मुंबई",
        "lang": "Hindi"
    })
    assert rv.status_code == 200
    assert rv.get_json()['success'] is True
    assert 'AI Personalized Tip (Hindi)' in rv.get_json()['message']

def test_database_candidates_and_voting_flow(client):
    """Test full database voting flow: registration -> get candidates -> cast vote -> double voting check -> results"""
    # 1. Register Voter
    rv_gen = client.post('/generate', json={
        "name": "Database Test Voter",
        "age": "30",
        "address": "456 DB Street"
    })
    assert rv_gen.status_code == 200
    voter_id = rv_gen.get_json().get('voter_id')
    assert voter_id is not None

    # 2. Get Candidates
    rv_cand = client.get('/candidates')
    assert rv_cand.status_code == 200
    candidates = rv_cand.get_json().get('candidates')
    assert len(candidates) > 0
    candidate_id = candidates[0]['id']

    # 3. Cast Vote
    rv_vote = client.post('/vote', json={
        "voter_id": voter_id,
        "candidate_id": candidate_id
    })
    assert rv_vote.status_code == 200
    assert rv_vote.get_json()['success'] is True
    assert 'Successfully Cast' in rv_vote.get_json()['message']

    # 4. Double Voting Prevention
    rv_vote_twice = client.post('/vote', json={
        "voter_id": voter_id,
        "candidate_id": candidate_id
    })
    assert rv_vote_twice.status_code == 200
    assert rv_vote_twice.get_json()['success'] is False
    assert 'already cast a vote' in rv_vote_twice.get_json()['message']

    # 5. Live Results
    rv_res = client.get('/results')
    assert rv_res.status_code == 200
    assert rv_res.get_json()['total_votes'] > 0

    # 6. Registered Voters List
    rv_voters = client.get('/voters')
    assert rv_voters.status_code == 200
    assert len(rv_voters.get_json()['voters']) > 0
