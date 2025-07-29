import zipfile
import itertools
import string
import time
import os
import multiprocessing
import random # 테스트용 임시 파일 생성을 위해 추가

# 전역 변수 선언 (초기화는 Manager를 통해 함수 안에서 이루어짐)
found_password = None
password_found_event = None


def generate_combinations(charset, length, start_idx, end_idx):
    """
    주어진 문자셋과 길이로 가능한 조합을 특정 범위만큼 생성하는 제너레이터
    """
    counter = 0
    for combination in itertools.product(charset, repeat=length):
        if counter >= start_idx and counter < end_idx:
            yield "".join(combination)
        counter += 1
        if counter >= end_idx:
            break

def unlock_zip_worker(zip_file_path, charset, length, start_index, end_index,
                      worker_id, found_password_val, found_event):
    """
    zip 파일의 암호를 풀기 위한 개별 워커(프로세스) 함수
    """
    start_time = time.monotonic()
    attempts = 0

    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zf:
            for password_attempt in generate_combinations(charset, length, start_index, end_index):
                if found_event.is_set():
                    print(f"워커 {worker_id}: 다른 워커가 비밀번호를 찾았어! 내 작업 종료!")
                    return

                attempts += 1
                try:
                    # extractall()을 시도하기 전에 listdir()로 파일 목록을 확인하는 편이 더 빠를 수 있음
                    # 실제 암호 해독 시도가 이루어지는 부분
                    zf.extractall(pwd=password_attempt.encode('utf-8'))
                    with found_password_val.get_lock():
                        found_password_val.value = password_attempt
                    found_event.set()
                    print(f"워커 {worker_id}: 야호! 비밀번호 찾았다: {password_attempt}")
                    return
                except (RuntimeError, zipfile.BadZipFile):
                    # 잘못된 비밀번호거나 zip 파일 손상
                    pass
                except Exception as e:
                    print(f"워커 {worker_id}: 압축 해제 중 알 수 없는 에러 발생: {e}")
                    return

    except FileNotFoundError:
        print(f"워커 {worker_id}: 야, '{zip_file_path}' 이 파일이 어디 갔니? 못 찾겠네.")
    except zipfile.BadZipFile:
        print(f"워커 {worker_id}: zip 파일이 손상되었거나 유효하지 않아.")
    except Exception as e:
        print(f"워커 {worker_id}: 예상치 못한 문제 발생: {e}")

    end_time = time.monotonic()
    duration = end_time - start_time
    # print(f"워커 {worker_id}: 내 작업 끝! {attempts}번 시도했고, {duration:.2f}초 걸렸어.") # 너무 많은 출력 방지


def create_test_zip_file(zip_file_name="test.zip", password_length=6):
    """
    테스트용 zip 파일을 생성하고 임의의 암호를 걸어준다.
    암호는 숫자와 소문자 알파벳으로 구성된 6자리이다.
    """
    charset = string.digits + string.ascii_lowercase
    test_password = ''.join(random.choice(charset) for _ in range(password_length))
    inner_file_name = "secret_message.txt"
    inner_file_content = f"이 파일의 비밀번호는 '{test_password}'이야!"

    print(f"\n--- 테스트용 zip 파일 생성 중 ---")
    print(f"생성될 zip 파일: {zip_file_name}")
    print(f"테스트용 암호: (잠시 후 브루트포스로 찾을 거야) '{test_password}'") # 실제 사용 시에는 이 줄은 삭제해야 함

    try:
        # 임시로 zip에 넣을 파일을 생성
        with open(inner_file_name, 'w', encoding='utf-8') as f:
            f.write(inner_file_content)

        # zip 파일 생성 및 암호화
        with zipfile.ZipFile(zip_file_name, 'w') as zf:
            # ZIP_DEFLATED는 압축 방식, ZIP_LZMA 등 다른 방식도 가능
            # 암호화는 'pwd' 인자를 사용
            zf.write(inner_file_name, arcname=inner_file_name,
                     compress_type=zipfile.ZIP_DEFLATED,
                     pwd=test_password.encode('utf-8'))
        print(f"'{zip_file_name}' 파일이 '{inner_file_name}'와 함께 암호 '{test_password}'로 생성되었어.")
        os.remove(inner_file_name) # 임시 파일 삭제
        return test_password # 생성된 암호를 반환 (테스트 확인용)
    except Exception as e:
        print(f"테스트용 zip 파일 생성 중 오류 발생: {e}")
        if os.path.exists(inner_file_name):
            os.remove(inner_file_name)
        return None


def unlock_zip(zip_file_path="test.zip", password_output_file="passwd_test.txt"):
    """
    지정된 zip 파일의 암호를 풀 수 있는 코드를 작성한다.
    암호는 특수 문자 없이 숫자와 소문자 알파벳으로 구성된 6자리 문자로 되어 있다.
    암호를 푸는 과정을 출력하고, 성공하면 암호를 지정된 파일에 저장한다.
    병렬 처리를 사용하여 암호를 더 빠르게 찾는다.
    """
    print("--- 암호 해독 시작! ---")
    start_overall_time = time.monotonic()

    charset = string.digits + string.ascii_lowercase
    password_length = 6

    total_combinations = len(charset) ** password_length
    print(f"가능한 암호 조합 수: {total_combinations:,}개")

    num_processes = multiprocessing.cpu_count()
    print(f"CPU 코어 {num_processes}개로 병렬 처리할 거야.")

    chunk_size = total_combinations // num_processes
    ranges = []
    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size
        if i == num_processes - 1:
            end_idx = total_combinations
        ranges.append((start_idx, end_idx))

    processes = []

    global found_password, password_found_event
    manager = multiprocessing.Manager()
    found_password = manager.Value(str, ' ' * password_length)
    password_found_event = manager.Event()


    for i, (start_idx, end_idx) in enumerate(ranges):
        p = multiprocessing.Process(
            target=unlock_zip_worker,
            args=(zip_file_path, charset, password_length, start_idx, end_idx,
                  i + 1, found_password, password_found_event)
        )
        processes.append(p)
        p.start()

    while any(p.is_alive() for p in processes) and not password_found_event.is_set():
        time.sleep(0.1)

    for p in processes:
        if p.is_alive():
            p.terminate()
            p.join()

    end_overall_time = time.monotonic()
    total_duration = end_overall_time - start_overall_time

    final_password = found_password.value.strip()

    if final_password != ' ' * password_length:
        print(f"\n--- 최종 결과: 암호 찾았다! ---")
        print(f"찾은 암호: {final_password}")
        print(f"총 소요 시간: {total_duration:.2f}초")
        try:
            with open(password_output_file, "w", encoding="utf-8") as f:
                f.write(final_password)
            print(f"암호를 '{password_output_file}' 파일에 저장했어.")
        except Exception as e:
            print(f"암호를 파일에 저장하다가 문제가 생겼어: {e}")
    else:
        print(f"\n--- 최종 결과: 암호를 못 찾았어... ---")
        print(f"총 소요 시간: {total_duration:.2f}초")
        print("이 범위 내에서는 암호를 찾을 수 없었어.")

if __name__ == "__main__":
    test_zip_file_name = "test.zip"
    password_output_file_name = "passwd_test.txt"

    # 1. 테스트용 zip 파일 생성
    # 이미 파일이 있다면 굳이 다시 만들지 않도록 예외 처리
    if not os.path.exists(test_zip_file_name):
        generated_password = create_test_zip_file(test_zip_file_name, password_length=6)
        if generated_password:
            print(f"테스트용 '{test_zip_file_name}' 파일이 성공적으로 생성되었어.")
        else:
            print("테스트용 zip 파일 생성에 실패했으니 해독을 시도하지 않을게.")
            exit() # 생성 실패 시 프로그램 종료
    else:
        print(f"경고: '{test_zip_file_name}' 파일이 이미 존재해. 기존 파일을 사용할 거야.")
        print("만약 새로운 테스트를 원하면 기존 파일을 삭제하고 다시 실행해 봐.")

    # 2. 브루트포스 복호화 시작
    unlock_zip(test_zip_file_name, password_output_file_name)

    # 선택 사항: 테스트 후 생성된 zip 파일 및 비밀번호 파일 정리
    # print("\n--- 테스트 후 정리 ---")
    # try:
    #     if os.path.exists(test_zip_file_name):
    #         os.remove(test_zip_file_name)
    #         print(f"'{test_zip_file_name}' 파일 삭제 완료.")
    #     if os.path.exists(password_output_file_name):
    #         os.remove(password_output_file_name)
    #         print(f"'{password_output_file_name}' 파일 삭제 완료.")
    # except Exception as e:
    #     print(f"파일 정리 중 오류 발생: {e}")