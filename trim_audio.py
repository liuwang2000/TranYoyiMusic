import os
import shutil
import subprocess
import re
from datetime import datetime
import configparser

# 复用项目路径配置
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
music_dir = os.path.join(base_dir, 'music')
old_music_dir = os.path.join(music_dir, 'old')

# 复用FFmpeg路径配置
ff_path = os.path.dirname(os.path.abspath(__file__))

# 检查FFmpeg可用性
ffmpeg_path = None
# 首先检查项目目录下的FFmpeg
local_ffmpeg_path = os.path.join(ff_path, 'ffmpeg-2025-03-24-git-cbbc927a67-essentials_build', 'bin')
if os.path.isfile(os.path.join(local_ffmpeg_path, 'ffmpeg.exe')):
    ffmpeg_path = local_ffmpeg_path
    os.environ['PATH'] = os.environ['PATH'] + os.pathsep + ffmpeg_path
    print(f"已检测到本地FFmpeg: {ffmpeg_path}")
else:
    # 如果本地没有，尝试系统PATH中的FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], check=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("已检测到系统FFmpeg")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"当前工作目录: {ff_path}")
        print(f"尝试的ffmpeg路径: {local_ffmpeg_path}")
        print("未检测到FFmpeg，请执行以下操作：")
        print("1. 运行install_ffmpeg.bat自动安装")
        print("2. 或手动下载FFmpeg并解压到项目目录")
        exit(1)

# 时间格式验证函数
def validate_time(input_time):
    # 支持分:秒格式（如2:30）和纯秒数格式
    pattern = r'^(\d+[:：]\d{1,2}(\.\d+)?|\d+(\.\d+)?)$'
    return re.match(pattern, input_time) is not None

def convert_to_seconds(time_str):
    # 将分:秒格式转换为秒数
    time_str = time_str.replace('：', ':')
    if ':' in time_str:
        minutes, seconds = time_str.split(':', 1)
        return float(minutes) * 60 + float(seconds)
    return float(time_str)

# 主处理流程
if __name__ == '__main__':
    try:
        # 选择音乐文件
        input_mp3 = input("请输入要剪辑的MP3文件路径: ").strip('"')
        
        if not os.path.isfile(input_mp3):
            print("无效的文件路径")
            exit(1)

        # 获取剪辑时间
        while True:
            start_time = input("请输入起始时间（秒或分:秒格式，0表示不剪切开头）: ").strip()
            if validate_time(start_time):
                # 转换为秒数
                start_seconds = convert_to_seconds(start_time)
                if start_seconds >= 0:
                    break
            print("时间格式错误，示例：3、3.5 或 2:30")

        while True:
            end_time = input("请输入结束时间（秒或分:秒格式，0表示不剪切结尾）: ").strip()
            if validate_time(end_time):
                # 转换为秒数
                end_seconds = convert_to_seconds(end_time)
                if end_seconds >= 0:
                    break
            print("时间格式错误，示例：120、120.5 或 5:30")

        # 生成备份文件名
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        original_name = os.path.basename(input_mp3)
        file_ext = os.path.splitext(original_name)[1]  # 获取原始文件的扩展名
        backup_name = f"{os.path.splitext(original_name)[0]}_原始_{timestamp}{file_ext}"
        
        # 移动原文件到备份目录
        # 确保备份目录存在
        os.makedirs(old_music_dir, exist_ok=True)
        shutil.move(input_mp3, os.path.join(old_music_dir, backup_name))
        
        # 构建FFmpeg命令
        ffmpeg_cmd = ['ffmpeg', '-i', os.path.join(old_music_dir, backup_name)]
        
        if start_time != '0':
            # 如果起始时间不为0，添加-ss参数
            ffmpeg_cmd += ['-ss', str(convert_to_seconds(start_time))]
        if end_time != '0':
            ffmpeg_cmd += ['-to', str(convert_to_seconds(end_time))]
        
        # 添加元数据编码参数解决中文乱码问题
        ffmpeg_cmd += ['-metadata:s:a:0', 'charset=UTF-8', '-c', 'copy', input_mp3]

        # 执行剪辑
        subprocess.run(ffmpeg_cmd, check=True)
        
        # 记录日志
        log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 剪辑文件: {original_name} | 起始: {start_time}s | 结束: {end_time}s\n"
        with open(os.path.join(ff_path, 'directory.log'), 'a', encoding='utf-8') as f:
            f.write(log_entry)

        print(f"\n剪辑完成：{original_name}\n新文件保存在: {input_mp3}\n")

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg处理失败: {str(e)}")
    except Exception as e:
        print(f"发生错误: {str(e)}")