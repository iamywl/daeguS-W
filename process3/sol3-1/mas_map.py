import pandas as pd
import os

FILE_STRUCT_CATEGORY = 'struct_category.csv'
FILE_AREA_MAP = 'area_map.csv'
FILE_AREA_STRUCT = 'area_struct.csv'


def load_csv_to_dataframe(file_path):
    try:
        df = pd.read_csv(file_path, sep = ',')
        print(f"\n--- '{file_path}' 파일 내용 ---")
        print(df.to_string(index = False))
        return df
    except FileNotFoundError:
        print(f"오류: '{file_path}' 파일을 찾을 수 없어. 현재 디렉토리에 파일이 있는지 확인해줘.")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        print(f"경고: '{file_path}' 파일이 비어 있어. 데이터가 없으면 분석할 수 없어.")
        return pd.DataFrame()
    except Exception as e:
        print(f"'{file_path}' 파일 읽기 중 알 수 없는 오류 발생: {e}")
        return pd.DataFrame()


def analyze_area_structures(area_struct_df, struct_category_df):
    if area_struct_df.empty or struct_category_df.empty:
        print("\n시설 분석을 위한 데이터가 부족해. area_struct.csv 또는 struct_category.csv가 비어있나봐.")
        return pd.DataFrame()

    merged_df = pd.merge(area_struct_df, struct_category_df,
                         left_on = 'category', right_on = 'category',
                         how = 'left')

    print("\n--- area_struct.csv와 struct_category.csv 병합 내용 (시설 이름 포함) ---")
    print(merged_df[['x', 'y', 'struct', 'area']].to_string(index = False))

    structure_counts = merged_df.dropna(subset = ['struct']).groupby(['area', 'struct']).size().reset_index(name = 'count')
    
    print("\n--- 각 Area별 시설 종류 집중 현황 ---")
    if not structure_counts.empty:
        print(structure_counts.to_string(index = False))
    else:
        print("시설 종류별 집중 현황 데이터가 없어.")

    total_structs_per_area = merged_df.groupby('area').size().reset_index(name = 'total_structures')
    
    print("\n--- 각 Area별 총 시설 개수 ---")
    if not total_structs_per_area.empty:
        print(total_structs_per_area.to_string(index = False))
    else:
        print("각 Area별 총 시설 개수 데이터가 없어.")

    return merged_df


def merge_all_data(area_map_df, area_struct_df, struct_category_df):
    if area_map_df.empty or area_struct_df.empty or struct_category_df.empty:
        print("\n모든 데이터를 병합하기 위한 데이터가 부족해. 모든 CSV 파일이 올바른지 확인해줘.")
        return pd.DataFrame()

    merged_struct_category = pd.merge(area_struct_df, struct_category_df,
                                      left_on = 'category', right_on = 'category',
                                      how = 'left')

    final_merged_df = pd.merge(area_map_df, merged_struct_category,
                               on = ['x', 'y'],
                               how = 'left')
    
    print("\n--- 모든 CSV 파일 병합 결과 ---")
    print(final_merged_df.to_string(index = False))
    
    return final_merged_df


def filter_and_display_area_data(merged_data_df, target_area_id):
    if merged_data_df.empty:
        print("\n필터링할 데이터가 없어.")
        return pd.DataFrame()

    area_filtered_df = merged_data_df[merged_data_df['area'] == target_area_id]

    print(f"\n--- Area {target_area_id} 데이터만 필터링한 결과 ---")
    if not area_filtered_df.empty:
        print(area_filtered_df.to_string(index = False))
    else:
        print(f"Area {target_area_id}에 해당하는 데이터가 없어.")

    return area_filtered_df


def generate_structure_report(filtered_area_data, area_id):
    if filtered_area_data.empty:
        print(f"\nArea {area_id}에 대한 리포트를 생성할 데이터가 없어.")
        return

    print(f"\n--- Area {area_id} 시설 및 지형 요약 리포트 ---")

    terrain_info = filtered_area_data[['x', 'y', 'mountain']].drop_duplicates().reset_index(drop = True)
    if not terrain_info.empty:
        print("\n[지형 정보 (mountain: 1은 산악 지대, 0은 일반 지대)]")
        print(terrain_info.to_string(index = False))
    else:
        print("\n[지형 정보] 없음")

    structures_summary = filtered_area_data.dropna(subset = ['struct']).groupby('struct').size().reset_index(name = 'count')
    if not structures_summary.empty:
        print("\n[시설 종류별 개수]")
        print(structures_summary.to_string(index = False))
    else:
        print("\n[시설 종류] 없음 (해당 Area에 시설물이 없거나 데이터 오류)")

    detailed_structures = filtered_area_data[['struct', 'x', 'y']].dropna(subset = ['struct']).reset_index(drop = True)
    if not detailed_structures.empty:
        print("\n[각 시설의 상세 위치]")
        print(detailed_structures.to_string(index = False))
    else:
        print("\n[상세 시설 위치] 없음 (해당 Area에 시설물이 없거나 데이터 오류)")


if __name__ == '__main__':
    struct_category_df = load_csv_to_dataframe(FILE_STRUCT_CATEGORY)
    area_map_df = load_csv_to_dataframe(FILE_AREA_MAP)
    area_struct_df = load_csv_to_dataframe(FILE_AREA_STRUCT)

    if not (area_map_df.empty or area_struct_df.empty or struct_category_df.empty):
        merged_struct_info_df = analyze_area_structures(area_struct_df, struct_category_df)

        all_merged_df = merge_all_data(area_map_df, area_struct_df, struct_category_df)

        target_area_id = 1
        if not all_merged_df.empty:
            area1_filtered_df = filter_and_display_area_data(all_merged_df, target_area_id)

            generate_structure_report(area1_filtered_df, target_area_id)
    else:
        print("\n필요한 CSV 파일 중 일부가 없거나 비어 있어서 분석을 진행할 수 없어. 파일을 확인해봐.")