#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import argparse
from datetime import datetime

# 设置终端编码为UTF-8
if hasattr(sys, 'stdout'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python 3.6及更早版本
        pass

def clean_filename(filename):
    """移除文件名中的非法字符和Emoji，替换为下划线"""
    # Windows文件名不允许的字符: < > : " / \ | ? *
    invalid_chars = r'[<>:"/\\|?*]'
    # 新增手势符号范围
    emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'\
                    r'\U0001F1E0-\U0001F1FF\U0001F900-\U0001F9FF\u2600-\u26FF\u2700-\u27BF'\
                    r'\U0001FA00-\U0001FAFF]'  # 新增手势符号范围
    # 合并替换非法字符和Emoji
    cleaned = re.sub(f'({invalid_chars}|{emoji_pattern})', '_', filename)
    # 移除文件名开头和结尾的空格和点
    cleaned = cleaned.strip('. ')
    # 如果文件名变为空，则使用默认名称
    if not cleaned or cleaned == '.':
        return 'unnamed_file'
    return cleaned

def rename_files(directory, recursive=False, log_file=None, dry_run=False):
    """重命名指定目录下含有非法字符的文件"""
    renamed_count = 0
    failed_count = 0
    skipped_count = 0
    
    if not os.path.isdir(directory):
        print(f"错误：'{directory}' 不是有效目录")
        return renamed_count, failed_count, skipped_count
    
    # 记录开始时间
    start_time = datetime.now()
    
    # 打开日志文件
    log_fh = None
    if log_file:
        try:
            log_fh = open(log_file, 'a', encoding='utf-8')
            log_fh.write(f"\n--- 开始于 {start_time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            log_fh.write(f"扫描目录: {os.path.abspath(directory)}\n")
        except Exception as e:
            print(f"无法打开日志文件: {e}")
            log_fh = None
    
    # 遍历目录
    for root, dirs, files in os.walk(directory):
        for filename in files:
            original_filepath = os.path.join(root, filename)
            cleaned_filename = clean_filename(filename)
            
            # 如果文件名需要清理
            if filename != cleaned_filename:
                new_filepath = os.path.join(root, cleaned_filename)
                
                # 检查新文件名是否已存在
                counter = 1
                base_name, extension = os.path.splitext(cleaned_filename)
                while os.path.exists(new_filepath):
                    # 如果文件已存在，添加数字后缀
                    cleaned_filename = f"{base_name}_{counter}{extension}"
                    new_filepath = os.path.join(root, cleaned_filename)
                    counter += 1
                
                # 输出重命名信息
                print(f"发现非法文件名: {filename}")
                print(f"将重命名为: {cleaned_filename}")
                
                # 记录到日志
                if log_fh:
                    log_fh.write(f"重命名: '{original_filepath}' -> '{new_filepath}'\n")
                
                # 执行重命名
                if not dry_run:
                    try:
                        os.rename(original_filepath, new_filepath)
                        print(f"重命名成功: {original_filepath} -> {new_filepath}")
                        renamed_count += 1
                    except Exception as e:
                        print(f"重命名失败: {e}")
                        if log_fh:
                            log_fh.write(f"失败: '{original_filepath}' - {str(e)}\n")
                        failed_count += 1
                else:
                    print("预演模式: 不执行实际重命名")
                    skipped_count += 1
            
        # 如果不是递归模式，只处理顶层目录
        if not recursive:
            break
    
    # 记录结束时间和统计信息
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # 打印和记录统计信息
    summary = f"\n完成扫描! 耗时: {duration:.2f}秒\n"
    summary += f"总计: 重命名 {renamed_count} 个文件"
    if failed_count > 0:
        summary += f", 失败 {failed_count} 个文件"
    if skipped_count > 0:
        summary += f", 跳过 {skipped_count} 个文件（预演模式）"
    
    print(summary)
    
    if log_fh:
        log_fh.write(summary + "\n")
        log_fh.write(f"--- 结束于 {end_time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        log_fh.close()
    
    return renamed_count, failed_count, skipped_count

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='重命名包含非法字符的文件', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-r', '--recursive', action='store_true', 
                        help='递归扫描所有子目录')
    parser.add_argument('-l', '--log', default='rename_log.txt',
                        help='日志文件路径 (默认为 rename_log.txt)')
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='预演模式，显示会被重命名的文件但不实际执行')
    
    args = parser.parse_args()
    
    # 交互式输入目录路径
    while True:
        directory = input("请输入要扫描的目录路径（直接回车使用当前目录）: ").strip()
        if not directory:
            directory = os.getcwd()
            break
        if os.path.isdir(directory):
            break
        print(f"错误：'{directory}' 不是有效目录，请重新输入\n")

    print(f"开始扫描目录: {os.path.abspath(directory)}")
    if args.recursive:
        print("启用递归模式，将扫描所有子目录")
    if args.dry_run:
        print("预演模式：不会实际重命名文件")
    
    # 执行重命名
    renamed, failed, skipped = rename_files(
        directory,  # 使用交互式输入的目录
        recursive=args.recursive,
        log_file=args.log,
        dry_run=args.dry_run
    )
    
    # 返回状态码
    return 1 if failed > 0 else 0

if __name__ == "__main__":
    sys.exit(main())