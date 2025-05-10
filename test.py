print('Hello Mars')
try:
    with open("./1-1-mission_computer_main.log", "r", encoding="utf-8") as exlog:
        line = exlog.readlines()
except Exception as err:
    print(f"오류발생 : {err}")