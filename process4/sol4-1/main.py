import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_spaceship_titanic():
    """
    Kaggle Spaceship Titanic 데이터를 분석하고 시각화하는 함수입니다.

    수행 과제:
    - train.csv, test.csv 파일을 읽어 병합합니다.
    - 전체 데이터 수량을 파악합니다.
    - Transported 항목과 가장 관련성이 높은 항목을 찾습니다.
    - 연령대별 Transported 여부를 그래프로 출력합니다.
    - (보너스) Destination 별 승객 연령대 분포를 시각화합니다.
    """

    # 1. 스페이스 타이타닉 데이터 파일 읽기
    # train.csv와 test.csv 파일이 현재 디렉토리에 있다고 가정합니다.
    try:
        train_df = pd.read_csv('train.csv')
        test_df = pd.read_csv('test.csv')
        print('INFO: train.csv 및 test.csv 파일 읽기 완료.')
    except FileNotFoundError:
        print('ERROR: train.csv 또는 test.csv 파일을 찾을 수 없습니다.')
        print('       Spaceship Titanic 데이터를 다운로드하여 현재 디렉토리에 압축을 해제해주세요.')
        return

    # 2. 두 파일을 하나로 병합
    # test 데이터셋에는 'Transported' 컬럼이 없으므로, 병합 시 None으로 채워 분석에 활용합니다.
    merged_df = pd.concat([train_df.assign(source='train'), test_df.assign(source='test', Transported=None)], ignore_index=True)
    print('\nINFO: train.csv와 test.csv 파일 병합 완료.')

    # 3. 전체 데이터 수량 파악
    total_data_count = len(merged_df)
    print(f'INFO: 전체 데이터 수량: {total_data_count} 건')

    # 4. Transported 항목과 가장 관련성이 높은 수치형 항목 찾기
    # 'Transported' 컬럼을 숫자로 변환하여 상관관계를 계산합니다 (True: 1, False: 0).
    train_df_for_corr = train_df.copy()
    train_df_for_corr['Transported_numeric'] = train_df_for_corr['Transported'].astype(int)

    # 수치형 컬럼만 선택하여 상관관계 계산
    numeric_cols = train_df_for_corr.select_dtypes(include=['number']).columns
    correlation_matrix = train_df_for_corr[numeric_cols].corr()

    # 'Transported_numeric' 컬럼과의 상관관계 절댓값으로 정렬
    if 'Transported_numeric' in correlation_matrix.columns:
        transported_corr = correlation_matrix['Transported_numeric'].abs().sort_values(ascending=False)
        print('\nINFO: Transported 항목과 가장 관련성이 높은 수치형 항목:')
        print(transported_corr)
        # 'Transported_numeric' 자기 자신을 제외하고 가장 높은 상관관계를 가진 항목을 찾습니다.
        most_correlated_numeric = transported_corr.index[1] if len(transported_corr) > 1 else 'N/A'
        print(f"INFO: 가장 관련성이 높은 수치형 항목 (Transported_numeric 제외): '{most_correlated_numeric}'")
    else:
        print('WARN: Transported_numeric 컬럼이 상관관계 계산에 포함되지 않았습니다.')
        most_correlated_numeric = 'N/A'

    print('\nINFO: 범주형 항목과 Transported의 관계는 시각화를 통해 파악하는 것이 좋습니다.')
    print('      예: HomePlanet, CryoSleep, Destination, VIP, Deck 등')


    # 5. 나이를 기준으로 연령대별 Transported 여부를 그래프로 출력
    # 'Age' 컬럼의 결측치 처리 (중앙값으로 대체)
    # Pandas FutureWarning를 피하기 위해 할당 연산자를 사용합니다.
    train_df['Age'] = train_df['Age'].fillna(train_df['Age'].median())

    # 연령대(Age Group) 컬럼 생성
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 100]
    labels = ['<10', '10s', '20s', '30s', '40s', '50s', '60s', '70s+']
    train_df['AgeGroup'] = pd.cut(train_df['Age'], bins=bins, labels=labels, right=False)

    # 연령대별 Transported 비율 계산 (observed=False를 명시하여 FutureWarning 방지)
    age_transported_rate = train_df.groupby('AgeGroup', observed=False)['Transported'].value_counts(normalize=True).unstack().fillna(0)

    # 그래프 출력 및 파일 저장
    plt.figure(figsize=(10, 6))
    age_transported_rate.plot(kind='bar', stacked=True, color=['lightcoral', 'skyblue'], ax=plt.gca())
    plt.title('Transported Status by Age Group')
    plt.xlabel('Age Group')
    plt.ylabel('Proportion')
    plt.xticks(rotation=45)
    plt.legend(title='Transported', labels=['No', 'Yes'])
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('age_group_transported.png') # 그래프를 파일로 저장
    print('\nINFO: 연령대별 Transported 여부 그래프 출력 완료 (age_group_transported.png).')


    # 보너스 과제: Destination 별로 승객들의 연령대 분포를 시각화
    # 'Destination' 컬럼의 결측치 처리 (최빈값으로 대체)
    # Pandas FutureWarning를 피하기 위해 할당 연산자를 사용합니다.
    train_df['Destination'] = train_df['Destination'].fillna(train_df['Destination'].mode()[0])

    # 바이올린 플롯으로 연령대 분포 및 Transported 여부 시각화
    plt.figure(figsize=(12, 7))
    # palette 키를 실제 불리언 값(True, False)으로 변경하여 ValueError 해결
    sns.violinplot(x='Destination', y='Age', hue='Transported', data=train_df, palette={True: 'skyblue', False: 'lightcoral'}, split=True)
    plt.title('Age Distribution by Destination and Transported Status (Violin Plot)')
    plt.xlabel('Destination')
    plt.ylabel('Age')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('destination_age_transported_violin.png')
    print('\nINFO: Destination 별 승객 연령대 분포 (Violin Plot) 시각화 완료 (destination_age_transported_violin.png).')

    # 박스 플롯으로 연령대 분포 및 Transported 여부 시각화
    plt.figure(figsize=(12, 7))
    sns.boxplot(x='Destination', y='Age', data=train_df, hue='Transported', palette={True: 'skyblue', False: 'lightcoral'})
    plt.title('Age Distribution by Destination (Box Plot)')
    plt.xlabel('Destination')
    plt.ylabel('Age')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('destination_age_transported_box.png')
    print('\nINFO: Destination 별 승객 연령대 분포 (Box Plot) 시각화 완료 (destination_age_transported_box.png).')

    # 히스토그램으로 Destination 별 연령대 분포 시각화 (Transported와 무관하게)
    plt.figure(figsize=(12, 7))
    sns.histplot(data=train_df, x='Age', hue='Destination', multiple='stack', bins=bins, palette='viridis')
    plt.title('Age Distribution by Destination (Stacked Histogram)')
    plt.xlabel('Age')
    plt.ylabel('Count')
    plt.xticks(bins[:-1], labels, rotation=45)
    plt.legend(title='Destination')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('destination_age_histogram.png')
    print('\nINFO: Destination 별 연령대 분포 (Histogram) 시각화 완료 (destination_age_histogram.png).')

# 스크립트 실행 시 함수 호출
if __name__ == '__main__':
    analyze_spaceship_titanic()