#!/bin/bash

# 1. 현재 디렉토리에 'doc' 디렉토리 생성
echo "doc 디렉토리 생성 시도..."
if [ ! -d "doc" ]; then
    mkdir -p doc
    echo "doc 디렉토리가 생성되었습니다."
else
    echo "doc 디렉토리가 이미 존재합니다. 생성을 건너뜀."
fi

# 2. doc 디렉토리 안으로 이동
#cd doc

# 3. process1 ~ process10 디렉토리 생성
for i in {1..10}; do
    process_dir="process${i}"
    echo "${process_dir} 디렉토리 생성 시도..."
    if [ ! -d "$process_dir" ]; then
        mkdir -p "$process_dir"
        echo "${process_dir} 디렉토리가 생성되었습니다."
    else
        echo "${process_dir} 디렉토리가 이미 존재합니다. 생성을 건너뜀."
    fi

    # 4. 각 process 디렉토리 안에 solN-1 ~ solN-10 디렉토리 생성
    for j in {1..10}; do
        sol_dir="sol${i}-${j}"
        echo "  ${process_dir}/${sol_dir} 디렉토리 생성 시도..."
        if [ ! -d "${process_dir}/${sol_dir}" ]; then
            mkdir -p "${process_dir}/${sol_dir}"
            echo "  ${process_dir}/${sol_dir} 디렉토리가 생성되었습니다."
        else
            echo "  ${process_dir}/${sol_dir} 디렉토리가 이미 존재합니다. 생성을 건너뜀."
        fi
    done
done

echo "DONE"
