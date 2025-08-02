import argparse
import json
from tabulate import tabulate


def parse_command_line() -> argparse.Namespace:
    """Функция для обработки команды в командной строке."""

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="path to the log file",
                        type=str, nargs="*")
    parser.add_argument("--report", help="",
                        type=str, choices=["average"])

    args = parser.parse_args()

    return args


def analyzes_log_files_average(paths: list[str]) -> list[dict]:
    """
    Функция для анализа файлов с логами. Находит количество эндпоинтов,
    общее время ответа и среднее время ответа по каждому эндпоинту.
    """

    result_data = []

    for path in paths:
        with open(path, "r") as file:
            for row_f in file:
                row_file = json.loads(row_f)

                if row_file.get("status") == 200:

                    if row_file.get("url") not in (row.get("url") for row in result_data):
                        result_data.append({"url": row_file.get("url"),
                                            "sum_response_time": row_file.get("response_time"),
                                            "count": 1})

                    else:
                        for row in result_data:
                            if row.get("url") == row_file.get("url"):
                                row["sum_response_time"] += row_file.get("response_time")
                                row["count"] += 1

    for data in result_data:
        sum_response_time = data.get("sum_response_time")
        count = data.get("count")

        avg_response_time = sum_response_time / count
        data["avg_response_time"] = avg_response_time

    return result_data


def display_average(data: list[dict]) -> None:
    """Функция для настройки отображения результата. Печатает результат в консоль."""

    for row in data:
        row.pop("sum_response_time")

    print(tabulate(data, headers="keys", showindex="always", floatfmt=".3f"))


def main() -> None:
    """Основная функция запуска скрипта."""

    command_line_args = parse_command_line()

    if command_line_args.report == "average":
        if command_line_args.file:
            log_data = analyzes_log_files_average(command_line_args.file)
            display_average(log_data)
        else:
            raise ValueError("Path not specified. Specify the path to the file or files.")


if __name__ == "__main__":
    main()
