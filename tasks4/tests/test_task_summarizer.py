import pytest
from unittest.mock import Mock, MagicMock
from tasks4 import TaskSummarizer


@pytest.fixture
def mock_openai_client(monkeypatch):
    """Fixture to mock OpenAI client"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.output_text = "Mocked summary"
    mock_client.responses.create.return_value = mock_response
    
    # Mock the OpenAI constructor
    mock_openai = Mock(return_value=mock_client)
    monkeypatch.setattr("tasks4.OpenAI", mock_openai)
    
    return mock_client


@pytest.fixture
def summarizer(mock_openai_client):
    """Fixture providing a TaskSummarizer instance with mocked client"""
    return TaskSummarizer(api_key="test_key")


def test_task_summarizer_initialization():
    """Test that TaskSummarizer initializes correctly"""
    summarizer = TaskSummarizer(api_key="test_key", model="gpt-4.1")
    assert summarizer.model == "gpt-4.1"


def test_summarize_task_calls_api(summarizer, mock_openai_client):
    """Test that summarize_task calls the OpenAI API correctly"""
    task = "Make a video game"
    result = summarizer.summarize_task(task)
    
    # Verify API was called
    mock_openai_client.responses.create.assert_called_once()
    
    # Verify the call parameters
    call_args = mock_openai_client.responses.create.call_args
    assert call_args.kwargs["model"] == "gpt-4.1-mini"
    assert task in call_args.kwargs["input"][0]["content"]
    
    # Verify return value
    assert result == "Mocked summary"


def test_summarize_task_with_empty_string(summarizer, mock_openai_client):
    """Test summarizing an empty task"""
    result = summarizer.summarize_task("")
    assert result == "Mocked summary"
    mock_openai_client.responses.create.assert_called_once()


def test_summarize_multiple_tasks(summarizer, mock_openai_client):
    """Test summarizing multiple tasks"""
    tasks = [
        "Make a video game",
        "Build a PC",
        "Write a novel"
    ]
    
    results = summarizer.summarize_tasks(tasks)
    
    # Verify API was called for each task
    assert mock_openai_client.responses.create.call_count == 3
    
    # Verify we got summaries for all tasks
    assert len(results) == 3
    assert all(r == "Mocked summary" for r in results)


def test_summarize_tasks_empty_list(summarizer):
    """Test summarizing an empty list of tasks"""
    results = summarizer.summarize_tasks([])
    assert results == []


def test_print_summaries(summarizer, mock_openai_client, capsys):
    """Test that print_summaries outputs correctly"""
    tasks = ["Task 1", "Task 2"]
    
    summarizer.print_summaries(tasks)
    
    # Capture printed output
    captured = capsys.readouterr()
    
    # Verify output format
    assert "Task 1 summary:" in captured.out
    assert "Task 2 summary:" in captured.out
    assert "Mocked summary" in captured.out


def test_api_error_handling(monkeypatch):
    """Test handling of API errors"""
    # Mock OpenAI to raise an exception
    mock_client = Mock()
    mock_client.responses.create.side_effect = Exception("API Error")
    
    mock_openai = Mock(return_value=mock_client)
    monkeypatch.setattr("tasks4.OpenAI", mock_openai)
    
    summarizer = TaskSummarizer(api_key="test_key")
    
    # Verify exception is raised
    with pytest.raises(Exception, match="API Error"):
        summarizer.summarize_task("Test task")


@pytest.mark.parametrize("task_length", [10, 100, 1000, 5000])
def test_summarize_various_lengths(summarizer, mock_openai_client, task_length):
    """Test summarizing tasks of various lengths"""
    task = "a" * task_length
    result = summarizer.summarize_task(task)
    
    assert result == "Mocked summary"
    mock_openai_client.responses.create.assert_called_once()