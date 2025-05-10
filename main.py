print('Hello Mars')

err_keywords = ["unstable", "explosion", "powered down"]

try:
    matched_lines = []
    with open("1-1-mission_computer_main.log", "r", encoding="utf-8") as logfile:
        for line in logfile:
            if any(err_keywords in line.lower() for err_keywords in err_keywords):
                matched_lines.append(line)
    with open("log_analysis.md","w") as errlog:
        errlog.write("# Log 분석결과\n\n")
        if(matched_lines):
            errlog.write("## 문제 발생 로그\n\n")
            errlog.write("```\n")
            for i, log in enumerate(matched_lines, 1):
                errlog.write(f"{i}. '{log}'\n")
            errlog.write("```\n")
        else:
            errlog.write("에러로그 없음")

except FileExistsError:
    print("No logfile")
except exception as e:
    print("unexpected error : {e}")
   
#mission_computer_main.log의 내용을 통해서 사고의 원인을 분석하고 정리해서 보고서(log_analysis.md)를 Markdown 형태로 를 작성해 놓는다. 