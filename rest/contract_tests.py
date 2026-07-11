import uuid
import pytest
from unittest.mock import MagicMock, patch

from application.answer.answer_service import AnswerService, AnswerFilters
from application.answer.model.dto.answer import Answer
from application.models import Page


@pytest.fixture
def client(self):
    from application import app
    mock_service = MagicMock(spec=AnswerService)
    with app.test_client() as client:
        with app.app_context():
            with patch('application.answer.answer_controller.answers_service', mock_service):
                yield client, mock_service

@pytest.fixture
def created_answer(self):
    return Answer(
        id=uuid.UUID('67676767-6767-6767-6767-676767676767'),
        author_id=uuid.UUID('67676767-6767-6767-6767-676767676767'),
        question_id=uuid.UUID('76767676-7676-7676-7676-767676767676'),
        score=0,
        body='My answer'
    )
        
class TestCreateAnswer:
    def test_contract_request_format(self, client, created_answer):
        client, mock_service = client
        mock_service.create_answer.return_value = created_answer

        resp = client.post('/answers', json={
            'author_id': '67676767-6767-6767-6767-676767676767',
            'question_id': '76767676-7676-7676-7676-767676767676',
            'body': 'miumiumiu',
            'score': 0
        })

        assert resp.status_code == 201

    def test_contract_response_structure(self, client, created_answer):
        client, mock_service = client
        mock_service.create_answer.return_value = created_answer

        resp = client.post('/answers', json={
            'author_id': '67676767-6767-6767-6767-676767676767',
            'question_id': '76767676-7676-7676-7676-767676767676',
            'body': 'miumiumiu',
            'score': 0
        })

        data = resp.get_json()
        assert 'id' in data
        assert 'author_id' in data
        assert 'question_id' in data
        assert 'body' in data
        assert 'score' in data

    def test_contract_response_status_201(self, client, created_answer):
        client, mock_service = client
        mock_service.create_answer.return_value = created_answer

        resp = client.post('/answers', json={
            'body': 'test', 'score': 0
        })

        assert resp.status_code == 201

    def test_contract_service_called_correctly(self, client, created_answer):
        client, mock_service = client
        mock_service.create_answer.return_value = created_answer
        request_data = {
            'body': 'wiiwiwi',
            'score': 0,
            'author_id': '67676767-6767-6767-6767-676767676767'
        }

        client.post('/answers', json=request_data)

        mock_service.create_answer.assert_called_once_with(request_data)

    def test_contract_missing_body_field_still_accepted(self, client, created_answer):
        client, mock_service = client
        mock_service.create_answer.return_value = created_answer
        resp = client.post('/answers', json={'body': 'test'})
        assert resp.status_code == 201
        
@pytest.fixture
def client(self):
    from application import app
    mock_service = MagicMock(spec=AnswerService)
    with app.test_client() as client:
        with app.app_context():
            with patch('application.answer.answer_controller.answers_service', mock_service):
                yield client, mock_service

@pytest.fixture
def sample_page(self):
    answer = Answer(
        id=uuid.UUID('67676767-6767-6767-6767-676767676767'),
        author_id=uuid.UUID('76767676-7676-7676-7676-767676767676'),
        question_id=uuid.UUID('66667777-6666-7777-6666-676767676767'),
        score=5,
        body='answer'
    )
    return Page(size=10, page=1, total_pages=3, content=[answer])

class TestGetAnswers:
    def test_contract_request_query_params(self, client, sample_page):
        client, mock_service = client
        mock_service.get_answers.return_value = sample_page

        resp = client.get('/answers?author_id=a1&question_id=q1&page=1&size=10')

        assert resp.status_code == 200

    def test_contract_response_has_fields(self, client, sample_page):
        client, mock_service = client
        mock_service.get_answers.return_value = sample_page

        resp = client.get('/answers')
        data = resp.get_json()

        assert 'size' in data
        assert 'page' in data
        assert 'total_pages' in data
        assert 'content' in data

    def test_contract_content_is_array(self, client, sample_page):
        client, mock_service = client
        mock_service.get_answers.return_value = sample_page

        resp = client.get('/answers')
        data = resp.get_json()

        assert isinstance(data['content'], list)
        assert len(data['content']) > 0
        answer = data['content'][0]
        assert 'id' in answer
        assert 'body' in answer
        assert 'score' in answer

    def test_contract_values_match_request(self, client, sample_page):
        client, mock_service = client
        mock_service.get_answers.return_value = sample_page

        resp = client.get('/answers?page=1&size=10')
        data = resp.get_json()

        assert data['size'] == 10
        assert data['page'] == 1
        assert data['total_pages'] == 3

    def test_contract_status_200_on_success(self, client, sample_page):
        client, mock_service = client
        mock_service.get_answers.return_value = sample_page

        resp = client.get('/answers')

        assert resp.status_code == 200

    def test_contract_empty_params_accepted(self, client, sample_page):
        client, mock_service = client
        mock_service.get_answers.return_value = sample_page

        resp = client.get('/answers')

        assert resp.status_code == 200
