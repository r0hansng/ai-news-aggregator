import pytest
import json
from unittest.mock import MagicMock
from backend.features.digests.agents.curator_agent import CuratorAgent, RankedArticle

@pytest.fixture
def user_profile():
    return {
        "name": "Test User",
        "background": "Senior AI Engineer focusing on RAG",
        "expertise_level": "Advanced",
        "interests": ["Vector Databases", "LLM Fine-tuning"],
        "preferences": {"avoid_marketing": True}
    }

@pytest.fixture
def mock_digests():
    return [
        {"id": "1", "title": "Advanced RAG Patterns", "summary": "Deep dive into vector search.", "article_type": "technical"},
        {"id": "2", "title": "Intro to AI", "summary": "Basic concepts of neural networks.", "article_type": "tutorial"}
    ]

def test_curator_agent_system_prompt_building(user_profile):
    agent = CuratorAgent(user_profile)
    assert "Senior AI Engineer" in agent.system_prompt
    assert "Vector Databases" in agent.system_prompt
    assert "Advanced" in agent.system_prompt

def test_rank_digests_success(mocker, user_profile, mock_digests):
    # Mock the OpenAI client and its response
    mock_openai = mocker.patch("backend.features.digests.agents.curator_agent.OpenAI")
    mock_instance = mock_openai.return_value
    
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps({
            "articles": [
                {"digest_id": "1", "relevance_score": 9.5, "rank": 1, "reasoning": "Highly relevant to RAG focus."},
                {"digest_id": "2", "relevance_score": 3.0, "rank": 2, "reasoning": "Too basic for senior engineer."}
            ]
        })))
    ]
    mock_instance.chat.completions.create.return_value = mock_response

    agent = CuratorAgent(user_profile)
    results = agent.rank_digests(mock_digests)

    assert len(results) == 2
    assert results[0].digest_id == "1"
    assert results[0].relevance_score == 9.5
    assert results[1].digest_id == "2"
    assert results[1].rank == 2

def test_rank_digests_error_handling(mocker, user_profile, mock_digests):
    mock_openai = mocker.patch("backend.features.digests.agents.curator_agent.OpenAI")
    mock_instance = mock_openai.return_value
    mock_instance.chat.completions.create.side_effect = Exception("API Error")

    agent = CuratorAgent(user_profile)
    results = agent.rank_digests(mock_digests)

    # In production, we fallback to discovery order if the LLM fails
    assert len(results) == 2
    assert results[0].digest_id == "1"
    assert results[0].rank == 99
    assert "falling back" in results[0].reasoning.lower()
