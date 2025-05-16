print("Hello Mars")

import os

LOG_FILE = "1-1-mission_computer_main.log"
ERROR_LOG_MD = "log_analysis.md"
ERROR_ONLY_FILE = "errors_only.log"

err_keywords = ["unstable", "explosion", "powered down"]

try:
    # 전체 로그 출력
    print("\n[전체 로그 출력]")
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            print(line.strip())

    # 에러 키워드 필터링
    matched_lines = [
        line.strip()
        for line in lines
        if any(keyword in line.lower() for keyword in err_keywords)
    ]

    # 시간 역순 정렬
    matched_lines_sorted = sorted(
        matched_lines, key=lambda x: x.split(",")[0], reverse=True
    )

    # log_analysis.md 작성
    with open(ERROR_LOG_MD, "w", encoding="utf-8") as report:
        report.write("# Log 분석결과\n\n")
        if matched_lines_sorted:
            report.write("## 문제 발생 로그 (시간 역순)\n\n")
            report.write("```\n")
            for i, log in enumerate(matched_lines_sorted, 1):
                report.write(f"{i}. {log}\n")
            report.write("```\n")
        else:
            report.write("에러 로그 없음\n")

    # 문제 로그만 별도 저장
    with open(ERROR_ONLY_FILE, "w", encoding="utf-8") as errorfile:
        for log in matched_lines_sorted:
            errorfile.write(log + "\n")

    print("\n[✓] 분석 및 저장 완료")

except FileNotFoundError:
    print(f"[오류] 로그 파일 '{LOG_FILE}' 을 찾을 수 없습니다.")
except Exception as e:
    print(f"[예상치 못한 오류] {e}")
