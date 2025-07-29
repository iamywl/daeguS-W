import zipfile
import itertools
import string
import time
import os
import multiprocessing

# 전역 변수 선언은 그대로 두되, 초기화는 Manager를 통해 함수 안에서 하도록 변경
# 여기서 초기화를 하지 않음으로써 TypeError를 피한다.
# Manager 객체는 함수 호출 시 생성되므로, 여기에선 선언만 해둔다.
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
                    zf.extractall(pwd=password_attempt.encode('utf-8'))
                    with found_password_val.get_lock():
                        found_password_val.value = password_attempt
                    found_event.set()
                    print(f"워커 {worker_id}: 야호! 비밀번호 찾았다: {password_attempt}")
                    return
                except (RuntimeError, zipfile.BadZipFile):
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


def unlock_zip(zip_file_path="emergency_storage_key.zip"):
    """
    emergency_storage_key.zip 파일의 암호를 풀 수 있는 코드를 작성한다.
    암호는 특수 문자 없이 숫자와 소문자 알파벳으로 구성된 6자리 문자로 되어 있다.
    암호를 푸는 과정을 출력하고, 성공하면 암호를 password.txt로 저장한다.
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

    # 병렬 처리를 위한 공유 객체 초기화 (Manager를 통해 초기화)
    global found_password, password_found_event
    manager = multiprocessing.Manager() # Manager 객체 생성
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

    # 모든 프로세스가 끝날 때까지 기다리거나, 비밀번호가 발견될 때까지 기다린다.
    # Event가 설정되면 바로 종료하도록 한다.
    # 프로세스가 살아있는지 계속 체크하며 이벤트가 설정되었는지 본다.
    while any(p.is_alive() for p in processes) and not password_found_event.is_set():
        time.sleep(0.1) # 짧게 대기하며 CPU 점유율 낮춤

    # 비밀번호를 찾았거나 모든 프로세스가 종료되었으면 나머지 프로세스 종료
    for p in processes:
        if p.is_alive():
            p.terminate() # 강제 종료
            p.join() # 종료될 때까지 기다림

    end_overall_time = time.monotonic()
    total_duration = end_overall_time - start_overall_time

    final_password = found_password.value.strip()

    if final_password != ' ' * password_length:
        print(f"\n--- 최종 결과: 암호 찾았다! ---")
        print(f"찾은 암호: {final_password}")
        print(f"총 소요 시간: {total_duration:.2f}초")
        try:
            with open("password.txt", "w", encoding="utf-8") as f:
                f.write(final_password)
            print("암호를 'password.txt' 파일에 저장했어.")
        except Exception as e:
            print(f"암호를 파일에 저장하다가 문제가 생겼어: {e}")
    else:
        print(f"\n--- 최종 결과: 암호를 못 찾았어... ---")
        print(f"총 소요 시간: {total_duration:.2f}초")
        print("이 범위 내에서는 암호를 찾을 수 없었어.")

if __name__ == "__main__":
    target_zip_file = "emergency_storage_key.zip"

    if not os.path.exists(target_zip_file):
        print(f"경고: '{target_zip_file}' 파일이 현재 디렉토리에 없어.")
        print("테스트를 위해 이 이름의 암호화된 zip 파일을 직접 만들어야 해!")
        print("예: 'emergency_storage_key.zip' 파일을 만들고 암호를 'a1b2c3' 같은 걸로 설정해봐.")
    else:
        unlock_zip(target_zip_file)