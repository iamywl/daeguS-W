#!/bin/bash

# 1. 현재 디렉토리에 'doc' 디렉토리 생성
echo "Creating directory: doc/"
mkdir -p doc

# 2. doc 디렉토리 안으로 이동
cd doc

# 3. process1 ~ process10 디렉토리 생성
for i in {1..10}; do
    process_dir="process${i}"
    echo "Creating directory: ${process_dir}/"
    mkdir -p "$process_dir"

    # 4. 각 process 디렉토리 안에 solN-1 ~ solN-10 디렉토리 생성
    # 이때 solN-X의 N은 process 디렉토리 번호 (i)를 따름
    for j in {1..10}; do
        sol_dir="sol${i}-${j}" # 핵심: process 번호 (i)와 sol 순서 (j) 조합
        echo "  Creating subdirectory: ${process_dir}/${sol_dir}/"
        mkdir -p "${process_dir}/${sol_dir}"
    done
done

echo "Directory structure created successfully!"
