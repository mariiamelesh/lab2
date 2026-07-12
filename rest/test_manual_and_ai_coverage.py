import uuid
import pytest
from unittest.mock import MagicMock, patch

from application.answer.answer_service import AnswerService, AnswerFilters
from application.answer.model.dto.answer import Answer
from application.answer.model.mapper.answer_mapper import AnswerMapper
from application.models import Page

@pytest.fixture
def answer():
    mapper = AnswerMapper()

    mock_mapper = MagicMock(spec=AnswerMapper)
    service = AnswerService()
    service.answer_mapper = mock_mapper

    sample_uuid = uuid.UUID('67676767-6767-6767-6767-676767676760')

    valid_data = {
        'id': str(sample_uuid),
        'author_id': '6666666677777777',
        'question_id': '000000000',
        'body': 'meowmeowmoemow',
        'score': 67
    }

    data_without_id = {
        'author_id': '68686868',
        'question_id': '1010101010',
        'body': 'theres no id here XD',
        'score': 0
    }

    expected_answer = Answer(
        id=sample_uuid,
        author_id=uuid.UUID('67676767-6767-6767-6767-676767676760'),
        question_id=uuid.UUID('67676767-6767-6767-6767-676767676760'),
        score=67,
        body='meowmeowmoemow'
    )

    return {
        'mapper': mapper,
        'service': service,
        'mock_mapper': mock_mapper,
        'valid_data': valid_data,
        'data_without_id': data_without_id,
        'expected_answer': expected_answer,
    }


class TestAnswerCreation:
    def test_map_request_all_fields(self, answer):
        result = answer['mapper'].map_request(answer['valid_data'])
        assert result.id == answer['valid_data']['id']
        assert result.author_id == answer['valid_data']['author_id']
        assert result.body == answer['valid_data']['body']
        assert result.score == answer['valid_data']['score']

    def test_map_request_generates_id_when_missing(self, answer):
        result = answer['mapper'].map_request(answer['data_without_id'])
        assert isinstance(result.id, uuid.UUID)

    def test_create_returns_mapper_result(self, answer):
        answer['mock_mapper'].map_request.return_value = answer['expected_answer']
        result = answer['service'].create_answer(answer['valid_data'])
        assert result is answer['expected_answer']

    def test_create_delegates_to_mapper(self, answer):
        answer['mock_mapper'].map_request.return_value = answer['expected_answer']
        answer['service'].create_answer(answer['valid_data'])
        answer['mock_mapper'].map_request.assert_called_once_with(answer['valid_data'])

    def test_update_delegates_to_mapper(self, answer):
        answer['mock_mapper'].map_request.return_value = answer['expected_answer']
        answer['service'].update_answer(uuid.uuid4(), answer['valid_data'])
        answer['mock_mapper'].map_request.assert_called_once_with(answer['valid_data'])

    def test_update_returns_mapper_result(self, answer):
        answer['mock_mapper'].map_request.return_value = answer['expected_answer']
        result = answer['service'].update_answer(uuid.uuid4(), answer['valid_data'])
        assert result is answer['expected_answer']

    def test_map_entity_to_dto_preserves_fields(self, answer):
        entity = Answer(
            id=uuid.uuid4(),
            author_id=uuid.uuid4(),
            question_id=uuid.uuid4(),
            score=42,
            body='Entity body'
        )
        result = answer['mapper'].map_entity_to_dto(entity)
        assert result.id == entity.id
        assert result.author_id == entity.author_id
        assert result.question_id == entity.question_id
        assert result.score == 42
        assert result.body == 'Entity body'

    def test_map_entity_to_dto_returns_new_object(self, answer):
        entity = Answer(
            id=uuid.uuid4(),
            author_id=uuid.uuid4(),
            question_id=uuid.uuid4(),
            score=0,
            body='test'
        )
        result = answer['mapper'].map_entity_to_dto(entity)
        assert result is not entity
        
@pytest.fixture
def answer_search():
    service = AnswerService()

    filter_by_author = AnswerFilters(author_id='676767', question_id=None)
    filter_by_question = AnswerFilters(author_id=None, question_id='1010101')
    filter_by_both = AnswerFilters(author_id='000009999910000', question_id='67')
    filter_empty = AnswerFilters(author_id=None, question_id=None)

    return {
        'service': service,
        'filter_by_author': filter_by_author,
        'filter_by_question': filter_by_question,
        'filter_by_both': filter_by_both,
        'filter_empty': filter_empty,
    }
class TestAnswerSearch:
    def test_search_by_author_returns_page(self, answer_search):
        result = answer_search['service'].get_answers(
            answer_search['filter_by_author'], page=1, size=10
        )
        assert isinstance(result, Page)
        assert len(result.content) > 0

    def test_search_by_question_returns_page(self, answer_search):
        result = answer_search['service'].get_answers(
            answer_search['filter_by_question'], page=1, size=10
        )
        assert isinstance(result, Page)

    def test_search_with_both_filters(self, answer_search):
        result = answer_search['service'].get_answers(
            answer_search['filter_by_both'], page=1, size=10
        )
        assert isinstance(result, Page)

    def test_search_pagination_metadata(self, answer_search):
        result = answer_search['service'].get_answers(
            answer_search['filter_empty'], page=3, size=7
        )
        assert result.page == 3
        assert result.size == 7

    def test_get_answer_returns_correct_id(self, answer_search):
        answer_id = uuid.uuid4()
        result = answer_search['service'].get_answer(answer_id)
        assert result.id == answer_id

    def test_get_answers_returns_page_with_content(self, answer_search):
        result = answer_search['service'].get_answers(
            answer_search['filter_empty'], page=1, size=10
        )
        assert len(result.content) > 0
        assert isinstance(result.content[0], Answer)

    def test_page_to_json_has_required_fields(self, answer_search):
        result = answer_search['service'].get_answers(
            answer_search['filter_empty'], page=1, size=10
        )
        json_data = result.to_json()
        assert 'size' in json_data
        assert 'page' in json_data
        assert 'total_pages' in json_data
        assert 'content' in json_data

    def test_page_print_content_does_not_crash(self, answer_search):
        result = answer_search['service'].get_answers(
            answer_search['filter_empty'], page=1, size=10
        )
        result.print_content()
        
@pytest.fixture
def answer_edge_data():
    mapper = AnswerMapper()

    data_all_none = {
        'author_id': None,
        'question_id': None,
        'body': None,
        'score': None
    }

    data_negative_score = {
        'author_id': '6666667777777',
        'question_id': '12345 6 7 89',
        'body': 'miu miu 67',
        'score': -999
    }

    data_empty_id = {
        'id': '',
        'author_id': '676767676',
        'question_id': '1666777420',
        'body': 'Empty id',
        'score': 0
    }

    return {
        'mapper': mapper,
        'data_all_none': data_all_none,
        'data_negative_score': data_negative_score,
        'data_empty_id': data_empty_id,
    }


class TestAnswerEdgeCases:
    def test_none_fields_preserved_as_none(self, answer_edge_data):
        result = answer_edge_data['mapper'].map_request(answer_edge_data['data_all_none'])
        assert result.author_id is None
        assert result.question_id is None
        assert result.body is None
        assert result.score is None

    def test_negative_score_accepted(self, answer_edge_data):
        result = answer_edge_data['mapper'].map_request(answer_edge_data['data_negative_score'])
        assert result.score == -999

    def test_empty_id_generates_uuid(self, answer_edge_data):
        result = answer_edge_data['mapper'].map_request(answer_edge_data['data_empty_id'])
        assert isinstance(result.id, uuid.UUID)


# ═══════════════════════════════════════════════════════════════
# Нова фікстура: Контролер
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def answer_controller():
    """Flask test client з замоканим answers_service."""
    from application import app
    mock_service = MagicMock(spec=AnswerService)
    with app.test_client() as client:
        with app.app_context():
            with patch('application.answer.answer_controller.answers_service', mock_service):
                yield client, mock_service


class TestAnswerController:
    """Тести контролера — всі 4 ендпоінти + обидві гілки 404."""

    def test_post_returns_201(self, answer_controller):
        """POST /answers → 201."""
        client, mock = answer_controller
        mock.create_answer.return_value = Answer(
            id=uuid.uuid4(),
            author_id=uuid.uuid4(),
            question_id=uuid.uuid4(),
            score=0,
            body='test'
        )
        resp = client.post('/answers', json={'body': 'test', 'score': 0})
        assert resp.status_code == 201

    def test_get_answers_returns_200(self, answer_controller):
        """GET /answers → 200."""
        client, mock = answer_controller
        mock.get_answers.return_value = Page(
            size=10, page=1, total_pages=1,
            content=[Answer(id=uuid.uuid4(), author_id=uuid.uuid4(),
                           question_id=uuid.uuid4(), score=0, body='test')]
        )
        resp = client.get('/answers?page=1&size=10')
        assert resp.status_code == 200

    def test_get_answer_by_id_returns_200(self, answer_controller):
        """GET /answers/<id> → 200 коли answer знайдено."""
        client, mock = answer_controller
        mock.get_answer.return_value = Answer(
            id=uuid.uuid4(), author_id=uuid.uuid4(),
            question_id=uuid.uuid4(), score=5, body='found'
        )
        resp = client.get('/answers/some-id')
        assert resp.status_code == 200

    def test_get_answer_by_id_returns_404(self, answer_controller):
        """GET /answers/<id> → 404 коли answer не знайдено."""
        client, mock = answer_controller
        mock.get_answer.return_value = None
        resp = client.get('/answers/nonexistent')
        assert resp.status_code == 404
        assert resp.get_json()['error'] == 'Answer not found'

    def test_put_answer_returns_200(self, answer_controller):
        """PUT /answers/<id> → 200 коли answer знайдено."""
        client, mock = answer_controller
        mock.update_answer.return_value = Answer(
            id=uuid.uuid4(), author_id=uuid.uuid4(),
            question_id=uuid.uuid4(), score=5, body='updated'
        )
        resp = client.put('/answers/some-id', json={'body': 'updated'})
        assert resp.status_code == 200

    def test_put_answer_returns_404(self, answer_controller):
        """PUT /answers/<id> → 404 коли answer не знайдено."""
        client, mock = answer_controller
        mock.update_answer.return_value = None
        resp = client.put('/answers/nonexistent', json={'body': 'x'})
        assert resp.status_code == 404
        assert resp.get_json()['error'] == 'Answer not found'
