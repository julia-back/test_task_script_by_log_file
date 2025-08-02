import pytest
import json
from unittest.mock import patch, mock_open
from main import parse_command_line, analyzes_log_files_average, display_average, main


@pytest.fixture
def mock_log_data():
    """Функция для замены результата открытия файла с логами. Возвращает тестовые данные логов в виде строки."""

    logs = [
        {"url": "/api/1", "status": 200, "response_time": 0.1},
        {"url": "/api/1", "status": 200, "response_time": 0.2},
        {"url": "/api/2", "status": 200, "response_time": 0.3},
        {"url": "/api/1", "status": 404, "response_time": 0.4},
        {"url": "/api/2", "status": 200, "response_time": 0.5},
    ]

    return "\n".join(json.dumps(log) for log in logs)


@pytest.fixture
def mock_log_data2():
    """Функция для замены результата открытия файла с логами. Возвращает второй набор тестовых данных."""

    logs = [
        {"url": "/api/1", "status": 200, "response_time": 0.5},
        {"url": "/api/3", "status": 200, "response_time": 1.0},
    ]

    return "\n".join(json.dumps(log) for log in logs)


def test_parse_command_line():
    """Функция тестирования обработки командной строки."""

    test_args = ["--file", "file1.log", "file2.log", "--report", "average"]
    with patch("sys.argv", ["test.py"] + test_args):
        args = parse_command_line()
        assert args.file == ["file1.log", "file2.log"]
        assert args.report == "average"


def test_analyzes_log_files_average(mock_log_data):
    """Функция тестирования обработки файла с логами."""

    with patch("builtins.open", mock_open(read_data=mock_log_data)):
        result = analyzes_log_files_average(["test.log"])

    assert len(result) == 2

    api1_data = result[0]
    assert api1_data["sum_response_time"] == pytest.approx(0.3)
    assert api1_data["count"] == 2
    assert api1_data["avg_response_time"] == pytest.approx(0.15)

    api2_data = result[1]
    assert api2_data["sum_response_time"] == 0.8
    assert api2_data["count"] == 2
    assert api2_data["avg_response_time"] == 0.4


def test_display_average(capsys):
    """Функция тестирования вывода в консоль."""

    test_data = [
        {"url": "/api/1", "avg_response_time": 0.15, "count": 2, "sum_response_time": 0.3},
        {"url": "/api/2", "avg_response_time": 0.4, "count": 2, "sum_response_time": 0.8},
    ]

    display_average(test_data)

    captured = capsys.readouterr()
    assert "/api/1" in captured.out
    assert "/api/2" in captured.out
    assert "0.150" in captured.out
    assert "0.400" in captured.out
    assert "0.300" not in captured.out
    assert "0.800" not in captured.out


def test_main_with_mocked_files(mock_log_data, capsys):
    """Функция тестирования основной функции main()."""

    with (patch("sys.argv", ["test.py", "--report", "average", "--file", "test.log"]),
          patch("builtins.open", mock_open(read_data=mock_log_data))):

        main()

        captured = capsys.readouterr()
        assert "/api/1" in captured.out
        assert "/api/2" in captured.out
        assert "0.150" in captured.out
        assert "0.400" in captured.out


def test_main_no_files():
    """Функция обработки отстутствия файла."""

    with patch("sys.argv", ["test.py", "--report", "average"]), \
            pytest.raises(ValueError, match="Path not specified"):
        main()
