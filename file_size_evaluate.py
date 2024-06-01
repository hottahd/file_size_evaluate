#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime

def get_best_unit(size, unit_multipliers):
    for unit in reversed(['B', 'kB', 'MB', 'GB', 'TB', 'PB']):
        if size >= unit_multipliers[unit]:
            return unit
    return 'B'

def get_total_file_size(directory, unit=None):
    '''
    Evaluate total size of files in directory, avoiding symlink loops.
    
    Parameters:
       directory (str): directory path
       unit (str): unit of file size. Choose from 'B', 'kB', 'MB', 'GB', 'TB', 'PB'.
                   If None, the most appropriate unit will be chosen automatically.
    Returns:
       total_size (float): total size of files in directory in the specified unit
       chosen_unit (str): the unit that was used for the result
    '''
    
    unit_multipliers = {
        'B': 1,
        'kB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4,
        'PB': 1024**5
    }
    
    if unit is not None and unit not in unit_multipliers:
        raise ValueError(f"Invalid unit: {unit}. Choose from 'B', 'kB', 'MB', 'GB', 'TB', 'PB'.")
    
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory, followlinks=False):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                if not os.path.islink(filepath):
                    total_size += os.path.getsize(filepath)
                
                # 最適な単位を選択
                if unit is None:
                    display_unit = get_best_unit(total_size, unit_multipliers)
                else:
                    display_unit = unit

                converted_size = total_size / unit_multipliers[display_unit]
                print(f"\r{' '*50}\rCurrent total size: {converted_size:.2f} {display_unit}", end='', flush=True)
            except FileNotFoundError:
                # ファイルが見つからない場合は無視
                continue
    
    # 最終的な単位を選択
    if unit is None:
        unit = get_best_unit(total_size, unit_multipliers)
    
    final_size = total_size / unit_multipliers[unit]
    print(f"\nFinal total size: {final_size:.2f} {unit}")    
    
    return final_size, unit

def update_results_file(file_path, total_size, unit, caseid, dir_path):
    '''
    Update the results file with the size of a directory.
    
    Parameters:
       file_path (str): path to the results file
       total_size (float): total size of the directory
       unit (str): unit of the file size
       caseid (str): the case ID of the directory
       dir_path (str): the directory path
    '''
    # 現在の日時を取得
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # シンボリックリンクの場合の実体パスを取得
    if os.path.islink(dir_path):
        real_path = os.path.abspath(os.readlink(dir_path))
    else:
        real_path = os.path.abspath(dir_path)
    
    # 既存のデータを読み込む
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            existing_data = f.readlines()
    else:
        existing_data = []
    
    # データを辞書に変換
    existing_dict = {}
    for line in existing_data:
        parts = line.strip().rsplit(maxsplit=3)
        if len(parts) == 4:
            existing_caseid = parts[0]
            size = parts[1]
            timestamp = parts[2]
            path = parts[3]
            existing_dict[existing_caseid] = f"{size} {timestamp} {path}"
    
    # ディレクトリサイズの情報を更新
    directory_size_str = f"{total_size:6.2f} {unit}"
    existing_dict[caseid] = f"{directory_size_str} {now} {real_path}"
    
    # 更新されたデータを書き込む
    with open(file_path, 'w') as f:
        for caseid in sorted(existing_dict):
            size_timestamp_realpath = existing_dict[caseid]
            # フォーマット: ディレクトリ名、右揃えで6桁、小数点2桁、単位
            f.write(f"{caseid:<10} {size_timestamp_realpath}\n")

if __name__ == "__main__":
    # 引数が提供されていない場合はカレントディレクトリを使用
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = '.'

    # 指定されたディレクトリ以下のディレクトリを自動で取得し、ソート
    directories = sorted([d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))])

    results_file_path = 'filesize.txt'

    # ディレクトリサイズの計算と結果の保存
    for caseid in directories:
        print('\033[1m' + caseid + '\033[0m')
        dir_path = os.path.join(base_path, caseid)
        total_size, unit = get_total_file_size(dir_path)
        update_results_file(results_file_path, total_size, unit, caseid, dir_path)
