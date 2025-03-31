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

# 清理旧MP3文件
try:
    for mp3 in os.listdir(music_dir):
        if mp3.endswith('.mp3'):
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            new_name = f"{os.path.splitext(mp3)[0]}_{timestamp}.mp3"
            shutil.move(os.path.join(music_dir, mp3), 
            os.path.join(old_music_dir, new_name))
except Exception as e:
    print(f"清理旧MP3文件时出错: {str(e)}")

os.environ['PATH'] = os.environ['PATH'] + os.pathsep + r'C:\Program Files\FFmpeg\bin'
# 检查FFmpeg可用性
ffmpeg_path = None
for path in [
    os.path.join(ff_path, 'ffmpeg-2025-03-24-git-cbbc927a67-full_build\\bin'),
]:
    if os.path.isfile(os.path.join(path, 'ffmpeg.exe')):
        ffmpeg_path = path
        break

if ffmpeg_path:
    os.environ['PATH'] = os.environ['PATH'] + os.pathsep + ffmpeg_path
else:
    try:
        subprocess.run(['ffmpeg', '-version'], check=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"当前base_dir路径: {base_dir}")
        print(f"尝试的ffmpeg路径: {os.path.join(base_dir, 'ffmpeg-2025-03-24-git-cbbc927a67-full_build\\bin')}")
        print("未检测到FFmpeg，请执行以下操作：")
        print("1. 手动下载FFmpeg（https://www.gyan.dev/ffmpeg/builds/）")
        print("2. 解压后将bin目录添加到系统PATH环境变量")
        print("3. 或直接运行install_ffmpeg.bat自动安装")
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

while True:
    try:
        

        # 获取视频文件路径
        input_video = input("请输入视频文件完整路径: ").strip('"')
        
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
                for mp4 in os.listdir(video_dir):
                    if mp4.endswith('.mp4'):
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                        new_name = f"{os.path.splitext(mp4)[0]}_{timestamp}.mp4"
                        shutil.move(os.path.join(video_dir, mp4), 
                        os.path.join(old_video_dir, new_name))
            except Exception as e:
                print(f"清理旧mp4文件时出错: {str(e)}")

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