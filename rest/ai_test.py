
import uuid
import pytest
from application.answer.answer_service import AnswerService, AnswerFilters
from application.answer.model.dto.answer import Answer
from application.answer.model.mapper.answer_mapper import AnswerMapper
from application.models import Page


# ── AnswerMapper tests ──

class TestAnswerMapper:
    """Tests for AnswerMapper."""

    def test_map_request_with_all_fields(self):
        mapper = AnswerMapper()
        data = {
            'id': '12345678-1234-5678-1234-567812345678',
            'author_id': 'aaaa0000-0000-0000-0000-000000000001',
            'question_id': 'bbbb0000-0000-0000-0000-000000000002',
            'body': 'Test body',
            'score': 5
        }
        result = mapper.map_request(data)
        assert result.body == 'Test body'
        assert result.score == 5

    def test_map_request_without_id_generates_uuid(self):
        mapper = AnswerMapper()
        data = {
            'author_id': 'aaaa0000-0000-0000-0000-000000000001',
            'question_id': 'bbbb0000-0000-0000-0000-000000000002',
            'body': 'Hello',
            'score': 0
        }
        result = mapper.map_request(data)
        assert result.id is not None
        assert isinstance(result.id, uuid.UUID)

    def test_map_entity_to_dto(self):
        mapper = AnswerMapper()
        entity = Answer(
            id=uuid.uuid4(),
            author_id=uuid.uuid4(),
            question_id=uuid.uuid4(),
            score=10,
            body='entity body'
        )
        result = mapper.map_entity_to_dto(entity)
        assert result.id == entity.id
        assert result.author_id == entity.author_id
        assert result.question_id == entity.question_id
        assert result.body == 'entity body'
        assert result.score == 10


# ── AnswerService tests ──

class TestAnswerService:
    """Tests for AnswerService."""

    def setup_method(self):
        self.service = AnswerService()

    def test_create_answer(self):
        data = {
            'author_id': 'aaaa0000-0000-0000-0000-000000000001',
            'question_id': 'bbbb0000-0000-0000-0000-000000000002',
            'body': 'My answer',
            'score': 0
        }
        result = self.service.create_answer(data)
        assert result.body == 'My answer'

    def test_update_answer(self):
        data = {
            'author_id': 'aaaa0000-0000-0000-0000-000000000001',
            'question_id': 'bbbb0000-0000-0000-0000-000000000002',
            'body': 'Updated answer',
            'score': 5
        }
        result = self.service.update_answer(uuid.uuid4(), data)
        assert result.body == 'Updated answer'

    def test_get_answer(self):
        answer_id = uuid.uuid4()
        result = self.service.get_answer(answer_id)
        assert result.id == answer_id

    def test_get_answers_returns_page(self):
        filters = AnswerFilters(author_id=None, question_id=None)
        result = self.service.get_answers(filters, page=1, size=10)
        assert isinstance(result, Page)
        assert len(result.content) > 0


# ── AnswerFilters tests ──

class TestAnswerFilters:
    """Tests for AnswerFilters."""

    def test_filters_store_values(self):
        f = AnswerFilters(author_id='a1', question_id='q1')
        assert f.author_id == 'a1'
        assert f.question_id == 'q1'

    def test_filters_with_none(self):
        f = AnswerFilters(author_id=None, question_id=None)
        assert f.author_id is None
        assert f.question_id is None
