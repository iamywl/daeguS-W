# 파이썬 내장함수 any, ... Comprehension

```python
# test.log 파일 읽기
with open("test.log", "r") as logfile:
    for line in logfile:
        if any(keyword in line.lower() for keyword in keywords):
            matched_lines.append(line.strip())
```
파이썬의 문법은 매우 축약할 경우가 많아 가독성이 다소 떨어지는 경우가 있다.
예를 들어 특정로그 파일을 읽고, 해당 라인에 특정한 단어가 있는지 찾는 코드를 작성할 경우 위와 같이 작성할 수 있다.

```python
any(keyword in line.lower() for keyword in keywords):
```
나는 파이썬의 축약에 익숙하지 않아서 위와 같은 문법이 어색하다.


```python
for keyword in keywords:
    if keyword in line.lower():
        return True
return False
```
코드를 조금 풀어쓴다면, 위와 같이 풀어 쓸 수 있다.
위 코드의 의미는
키워드의 길이 만큼 반복하고:
만약에 키워드가 라인 소문자 안에 있다면, 리턴 True 아니면 False이다.
굳이 line,lower를 넣은 이유는 로그 파일의 경우 대문자 혹은 소문자가 섞여있는 경우가 있을 수 있다.
따라서 line을 모두 소문자로 변경하여 한번 더 키워드가 있는지 검증할 필요있다.

```python
    if keyword in line.lower():
```
코드의 기본적인 접근이 error 키워드를 배열에 저장하고 line을 체크해서 있을 경우 따로 저장하는 방식으로 구동된다.
이러한 방식은 대소문자를 엄격히 고려할 경우 explosion이라는 단어가 있는 행을 찾고 싶은 것인데 적어도 하나 이상의 대문자만 있어도 찾을 수 없는 문제가 있다.
이러한 경우를 대비하여 모두 소문자로 변경하여 검사하는 방법을 사용하였다.

## 🧐 why don't use upper()?

```python
err_keywords = ["unstable", "explosion", "powered down"]
```
물론 upper를 사용하여도 동일하게 대소문자와 구분없이 검증하는 과정을 구현할 수 있지만,
err_keywords에 소문자로 저장하여 모두 lower를 이용하여 검증하였다.


