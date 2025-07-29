import os
from datetime import datetime

log_file_name = "1-1-mission_computer_main.log"

def read_and_print_log(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as spacecraft_log:
            log_entries = spacecraft_log.readlines()

            print("\n--- 우주선 일지 원본 ---")
            for log_line in log_entries:
                print(log_line.strip())
            print("--- 일지 끝 ---")
            return log_entries

    except FileNotFoundError:
        print(f"야, {file_path} 이 파일이 어디 갔니? 못 찾겠네.")
        return None
    except Exception as big_accident:
        print(f"앗, 파일을 읽다가 사고가 났다: {big_accident}")
        return None

def sort_log_by_time_reverse(log_lines):
    if not log_lines:
        print("정렬할 로그 줄이 없어, 잉잉.")
        return []

    def extract_time_key(log_line):
        try:
            time_part = log_line[:23]
            return datetime.strptime(time_part, '%Y-%m-%d %H:%M:%S,%f')
        except (ValueError, IndexError) as time_parsing_error:
            print(f"시간 파싱하다가 문제 생김 ({log_line.strip()}): {time_parsing_error}")
            return datetime.min

    print("\n--- 우주선 일지 시간 역순 정렬 ---")
    sorted_log_lines = sorted(log_lines, key=extract_time_key, reverse=True)
    for log_line in sorted_log_lines:
        print(log_line.strip())
    print("--- 시간 역순 일지 끝 ---")
    return sorted_log_lines

def save_problem_events(log_lines, problem_file_name="problem_events.log"):
    if not log_lines:
        print("분석할 로그 줄이 없어, 헤헤.")
        return

    problem_lines = []
    for log_line in log_lines:
        if "ERROR" in log_line.upper() or "CRITICAL" in log_line.upper():
            problem_lines.append(log_line)

    if not problem_lines:
        print("문제가 되는 부분은 안 보이네. 다행이야!")
        return

    try:
        with open(problem_file_name, 'w', encoding='utf-8') as problem_file:
            for problem_line in problem_lines:
                problem_file.write(problem_line)
        print(f"\n문제가 되는 부분들을 '{problem_file_name}' 파일에 잘 저장했어.")
    except Exception as file_save_accident:
        print(f"문제 파일을 저장하다가 사고가 났다: {file_save_accident}")

if __name__ == "__main__":
    current_working_path = os.path.dirname(os.path.abspath(__file__))
    log_file_absolute_path = os.path.join(current_working_path, log_file_name)

    full_log_content = read_and_print_log(log_file_absolute_path)

    if full_log_content:
        sorted_log = sort_log_by_time_reverse(full_log_content)

        save_problem_events(full_log_content)