import os
import shutil
import subprocess
import re
from datetime import datetime
import configparser
import sys

# 设置终端编码为UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 初始化路径
ff_path = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
video_dir = os.path.join(base_dir, 'videos')
old_video_dir = os.path.join(video_dir, 'old')
music_dir = os.path.join(base_dir, 'music')
old_music_dir = os.path.join(music_dir, 'old')

# 创建必要目录
for d in [video_dir, old_video_dir, music_dir, old_music_dir]:
    try:
        os.makedirs(d, exist_ok=True)
    except OSError as e:
        print(f"创建目录失败: {d}\n错误信息: {str(e)}")
        exit(1)

# 用于移除文件名中的时间戳的函数
def remove_timestamp(filename):
    """移除文件名中的时间戳部分 (如 _20240331123456)"""
    basename, ext = os.path.splitext(filename)
    # 匹配 _数字(8-14位) 的模式，这通常是时间戳
    clean_name = re.sub(r'_\d{8,14}', '', basename)
    return clean_name + ext

# 清理旧MP3文件
try:
    mp3_count = 0
    mp3_files = [f for f in os.listdir(music_dir) if f.endswith('.mp3')]
    
    if mp3_files:
        print("初始化: 正在清理音乐目录...")
        
    for mp3 in mp3_files:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        clean_name = remove_timestamp(mp3)
        # 创建一个以清理后的文件名为基础的备份名
        backup_name = f"{os.path.splitext(clean_name)[0]}_{timestamp}.mp3"
        shutil.move(os.path.join(music_dir, mp3), 
        os.path.join(old_music_dir, backup_name))
        mp3_count += 1
    
    if mp3_count > 0:
        print(f"已清理 {mp3_count} 个音频文件")
except Exception as e:
    print("清理音频文件时出错")

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

def validate_date(input_date):
    cleaned = re.sub(r'\D', '', input_date)
    if len(cleaned) == 8:
        try:
            datetime.strptime(cleaned, '%Y%m%d')
            return cleaned
        except ValueError:
            pass
    return None

# 初始化配置
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# 首次运行获取作者信息
if not config.has_option('Metadata', 'TPE1') or not config.get('Metadata', 'TPE1'):
    TPE1_name = input("请输入作者名称: ").strip()
    TALB_name = input("请输入专辑名称: ").strip() or "未分类专辑"
    config['Metadata'] = {
        'TPE1': TPE1_name,
        'TALB': TALB_name,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open('config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)

# 初始化配置后立即获取元数据
TPE1_name = config.get('Metadata', 'TPE1')
TALB_name = config.get('Metadata', 'TALB')

def clean_processed_audio():
    """清理已处理过的音频文件，移动到old目录"""
    try:
        processed_count = 0
        processed_files = []
        
        # 先获取所有需要处理的文件列表
        files_to_process = []
        for audio in os.listdir(music_dir):
            if audio.endswith('.mp3') and not audio.startswith('temp_'):
                files_to_process.append(audio)
        
        # 如果没有文件需要处理，直接返回
        if not files_to_process:
            print("没有发现需要清理的音频文件")
            return
            
        print(f"开始清理音频文件，共 {len(files_to_process)} 个文件...")
            
        # 逐个处理文件
        for audio in files_to_process:
            try:
                source_path = os.path.join(music_dir, audio)
                # 检查文件是否仍然存在（可能被其他进程移动）
                if not os.path.exists(source_path):
                    continue
                    
                # 清理文件名中的时间戳
                clean_name = remove_timestamp(audio)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                new_name = f"{os.path.splitext(clean_name)[0]}_{timestamp}.mp3"
                dest_path = os.path.join(old_music_dir, new_name)
                
                # 移动文件但不输出详细信息
                shutil.move(source_path, dest_path)
                
                # 确认文件已成功移动
                if os.path.exists(dest_path):
                    processed_count += 1
                    processed_files.append(audio)
            except Exception as file_error:
                # 减少错误输出的详细程度
                print(f"移动文件失败: {audio}")
        
        # 简化输出结果
        if processed_count > 0:
            print(f"清理完成! 已成功移动 {processed_count} 个音频文件")
        else:
            print("没有文件被移动")
        
        # 记录清理操作到日志 (日志仍然保持详细记录，但不显示给用户)
        log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 清理操作 | 已移动 {processed_count} 个音频文件到 {old_music_dir}\n"
        if processed_files:
            log_entry += "已移动文件列表:\n"
            for file in processed_files:
                log_entry += f"  - {file}\n"
                
        with open(os.path.join(ff_path, 'directory.log'), 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
    except Exception as e:
        print(f"清理音频文件时出错: {str(e)}")
        # 简化错误信息输出
        # print(f"错误类型: {type(e).__name__}")
        # print(f"错误位置: {e.__traceback__.tb_frame.f_code.co_filename}, 行 {e.__traceback__.tb_lineno}")

while True:
    try:
        # 获取视频文件路径
        input_video = input("请输入视频文件完整路径 (输入'清理'移动处理过的文件，输入'退出'结束程序): ").strip('"')
        
        # 检查是否是退出命令
        if input_video.lower() in ['exit', 'quit', '退出']:
            print("程序已退出")
            break
        
        # 检查是否是清理命令
        if input_video.lower() in ['clean', '清理']:
            clean_processed_audio()
            continue
        
        if not os.path.isfile(input_video):
            print("无效的文件路径")
            continue
            
        # 移动视频到视频目录
        video_name = os.path.basename(input_video)
        shutil.move(input_video, os.path.join(video_dir, video_name))
        input_video = os.path.join(video_dir, video_name)

        # 生成临时MP3路径
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        temp_mp3 = os.path.join(music_dir, f"temp_{timestamp}.mp3")

        # 获取音乐信息
        TIT2_name = input("输入音乐名称（中文/英文）: ").strip()
        while True:
            input_date = input("输入时间（格式示例：2024.03.27或2024-03-27）: ")
            formatted_date = validate_date(input_date)
            if formatted_date:
                break
            print("日期格式不正确，请重新输入")

       # 提取音频
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_video,
            '-vn',
            '-acodec', 'libmp3lame',
            '-q:a', '2',
            '-map_metadata', '-1',
            '-metadata', f'TPE1={TPE1_name}',
            '-metadata', f'TALB={TALB_name}',
            '-metadata', f'TIT2={TIT2_name}',
            '-metadata', f'date={formatted_date}',
            '-id3v2_version', '3',
            temp_mp3
        ]
       
            
        subprocess.run(ffmpeg_cmd, check=True)
        # 生成最终文件名
        final_name = f"{TIT2_name}（{formatted_date}）.mp3"
        final_path = os.path.join(music_dir, final_name)
        
        # 移动文件并记录日志
        try:
            shutil.move(temp_mp3, final_path)
            # shutil.move(os.path.join(video_dir, video_name), os.path.join(old_video_dir, video_name))
            # 清理旧MP4文件
            try:
                processed_video_count = 0
                if any(f.endswith('.mp4') for f in os.listdir(video_dir)):
                    print("开始清理视频文件...")
                
                for mp4 in os.listdir(video_dir):
                    if mp4.endswith('.mp4'):
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                        # 清理文件名中的时间戳
                        clean_name = remove_timestamp(mp4)
                        new_name = f"{os.path.splitext(clean_name)[0]}_{timestamp}.mp4"
                        shutil.move(os.path.join(video_dir, mp4), 
                        os.path.join(old_video_dir, new_name))
                        processed_video_count += 1
                
                if processed_video_count > 0:
                    print(f"已清理 {processed_video_count} 个视频文件")
            except Exception as e:
                print("清理视频文件时出错")

            # 记录目录路径
            log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 作者: {TPE1_name} | 专辑: {TALB_name} | 音乐文件: {final_name} | 视频文件: {new_name} -> {old_video_dir}\n"
        except Exception as move_error:
            print(f"文件移动失败: {str(move_error)}")
            exit(1)
        with open(os.path.join(ff_path, 'directory.log'), 'a', encoding='utf-8') as f:
            f.write(log_entry)

        print(f"\n已处理：{final_name}\n")

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg处理失败: {str(e)}")
    except KeyboardInterrupt:
        print("\n操作已取消")
        break
    except Exception as e:
        print(f"发生未预期错误: {str(e)}")