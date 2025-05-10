print('Hello Mars')

err_keywords = ["unstable", "explosion", "powered down"]

try:
    with open("./1-1-mission_computer_main.log", "r", encoding="utf-8") as exlog:
        line = exlog.readlines()
        with open("log_analysis.md", "w") as f:

except Exception as err:
    print(f"오류발생 : {err}")

    