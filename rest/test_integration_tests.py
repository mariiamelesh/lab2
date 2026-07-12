import uuid
import pytest
from unittest.mock import MagicMock, patch

from application.answer.answer_service import AnswerService, AnswerFilters
from application.answer.model.dto.answer import Answer
from application.answer.model.mapper.answer_mapper import AnswerMapper
from application.models import Page

@pytest.fixture
def security_data():
    mapper = AnswerMapper()

    service = AnswerService()

    script = {
        'author_id': '67676767',
        'question_id': '6767667',
        'body': '<script>676767</script>',
        'score': 0
    }

    sql_injection = {
        'author_id': '676767',
        'question_id': '6767',
        'body': "DROP TABLE answers;",
        'score': 0
    }

    negative_score = {
        'author_id': '676767',
        'question_id': '67676767',
        'body': 'meowmoemwmeow',
        'score': -999
    }

    oversized_body = {
        'author_id': '6767676',
        'question_id': '666667777',
        'body': 'A' * 1000000,
        'score': 0
    }

    return {
        'mapper': mapper,
        'service': service,
        'script': script,
        'sql_injection': sql_injection,
        'negative_score': negative_score,
        'oversized_body': oversized_body,
    }


@pytest.fixture
def client():
    from application import app
    mock_service = MagicMock(spec=AnswerService)
    with app.test_client() as client:
        with app.app_context():
            with patch('application.answer.answer_controller.answers_service', mock_service):
                yield client, mock_service

class TestSecurityController:
    def test_post_without_json(self, client):
        client, _ = client
        resp = client.post('/answers', data='not json')
        assert resp.status_code in [400, 415]

    def test_post_with_invalid_json(self, client):
        client, _ = client
        resp = client.post('/answers',data='{invalid}', content_type='application/json')
        assert resp.status_code in [400, 500]

    def test_path_traversal_in_id_does_not_crash(self, client):
        client, mock_service = client
        mock_service.get_answer.return_value = None
        resp = client.get('/answer/67/76/00/etc/')
        assert resp.status_code != 500
        
        
class TestSecurityInput:
    def test_script_body(self, security_data):
        result = security_data['mapper'].map_request(security_data['script'])
        assert '<script>' not in result.body

    def test_sql_injection(self, security_data):
        result = security_data['mapper'].map_request(security_data['sql_injection'])
        assert 'DROP TABLE' not in result.body

    def test_negative_score(self, security_data):
        result = security_data['mapper'].map_request(security_data['negative_score'])
        assert result.score >= 0

    def test_oversized_body(self, security_data):
        result = security_data['mapper'].map_request(security_data['oversized_body'])
        assert len(result.body) <= 10000