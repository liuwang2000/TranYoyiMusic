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

# 存储上次输入的日期
last_input_date = ""

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
    audio_extensions = ['.mp3']
    mp3_files = [f for f in os.listdir(music_dir) if any(f.lower().endswith(ext) for ext in audio_extensions)]
    
    if mp3_files:
        print("初始化: 正在清理音乐目录...")
        
    for mp3 in mp3_files:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        clean_name = remove_timestamp(mp3)
        # 创建一个以清理后的文件名为基础的备份名，保留原始扩展名
        backup_name = f"{os.path.splitext(clean_name)[0]}_{timestamp}{os.path.splitext(mp3)[1]}"
        shutil.move(os.path.join(music_dir, mp3), 
        os.path.join(old_music_dir, backup_name))
        mp3_count += 1
    
    if mp3_count > 0:
        print(f"已清理 {mp3_count} 个音频文件")
except Exception as e:
    print(f"清理音频文件时出错: {str(e)}")

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
    """验证并提取日期，返回格式化日期和额外文本"""
    # 查找8位数字作为日期
    date_match = re.search(r'\d{8}', input_date)
    if date_match:
        # 提取匹配到的日期
        date_part = date_match.group(0)
        # 计算日期在原始字符串中的位置
        date_start = date_match.start()
        date_end = date_match.end()
        
        # 提取日期前后的文本
        prefix = input_date[:date_start].strip()
        suffix = input_date[date_end:].strip()
        
        # 组合额外文本
        extra_text = (prefix + " " + suffix).strip()
        
        try:
            # 验证日期格式
            datetime.strptime(date_part, '%Y%m%d')
            return date_part, extra_text
        except ValueError:
            return None, ""
    
    # 尝试从日期格式字符串中提取日期（如2024-09-13或2024.09.13）
    date_pattern = r'(\d{4})[-./年](\d{1,2})[-./月](\d{1,2})'
    date_match = re.search(date_pattern, input_date)
    if date_match:
        try:
            year = date_match.group(1)
            month = date_match.group(2).zfill(2)  # 确保月份是两位数
            day = date_match.group(3).zfill(2)    # 确保日期是两位数
            formatted_date = f"{year}{month}{day}"
            
            # 移除整个日期部分，保留其余文本作为额外文本
            full_date_str = date_match.group(0)  # 完整匹配的日期字符串
            extra_text = input_date.replace(full_date_str, "").strip()
            
            # 验证日期格式
            datetime.strptime(formatted_date, '%Y%m%d')
            return formatted_date, extra_text
        except (ValueError, IndexError):
            pass
    
    # 尝试从纯数字中提取日期
    cleaned = re.sub(r'\D', '', input_date)
    if len(cleaned) == 8:
        try:
            datetime.strptime(cleaned, '%Y%m%d')
            # 这里我们可能无法准确提取文本部分，因为无法确定哪些数字是日期的一部分
            # 尝试使用更智能的方法：寻找连续8位数字并移除
            date_pattern = r'\d{8}'
            extra_text = re.sub(date_pattern, '', input_date).strip()
            # 清理多余的分隔符
            extra_text = re.sub(r'[-_.,;:\s]+', ' ', extra_text).strip()
            return cleaned, extra_text
        except ValueError:
            pass
    
    # 如果没有找到有效日期，返回None和原始文本
    return None, input_date.strip()

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
        # 扩展支持的音频格式列表
        audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']
        for audio in os.listdir(music_dir):
            if any(audio.lower().endswith(ext) for ext in audio_extensions) and not audio.startswith('temp_'):
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
                new_name = f"{os.path.splitext(clean_name)[0]}_{timestamp}{os.path.splitext(audio)[1]}"
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

def clean_processed_videos():
    """清理已处理过的视频文件，移动到old目录"""
    try:
        processed_count = 0
        processed_files = []
        
        # 先获取所有需要处理的文件列表
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        files_to_process = []
        for video in os.listdir(video_dir):
            if any(video.lower().endswith(ext) for ext in video_extensions):
                files_to_process.append(video)
        
        # 如果没有文件需要处理，直接返回
        if not files_to_process:
            print("没有发现需要清理的视频文件")
            return
            
        print(f"开始清理视频文件，共 {len(files_to_process)} 个文件...")
            
        # 逐个处理文件
        for video in files_to_process:
            try:
                source_path = os.path.join(video_dir, video)
                # 检查文件是否仍然存在（可能被其他进程移动）
                if not os.path.exists(source_path):
                    continue
                    
                # 清理文件名中的时间戳
                clean_name = remove_timestamp(video)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                new_name = f"{os.path.splitext(clean_name)[0]}_{timestamp}{os.path.splitext(video)[1]}"
                dest_path = os.path.join(old_video_dir, new_name)
                
                # 移动文件但不输出详细信息
                shutil.move(source_path, dest_path)
                
                # 确认文件已成功移动
                if os.path.exists(dest_path):
                    processed_count += 1
                    processed_files.append(video)
            except Exception as file_error:
                # 减少错误输出的详细程度
                print(f"移动文件失败: {video}")
        
        # 简化输出结果
        if processed_count > 0:
            print(f"清理完成! 已成功移动 {processed_count} 个视频文件")
        else:
            print("没有视频文件被移动")
        
        # 记录清理操作到日志
        log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 视频清理操作 | 已移动 {processed_count} 个视频文件到 {old_video_dir}\n"
        if processed_files:
            log_entry += "已移动文件列表:\n"
            for file in processed_files:
                log_entry += f"  - {file}\n"
                
        with open(os.path.join(ff_path, 'directory.log'), 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
    except Exception as e:
        print(f"清理视频文件时出错: {str(e)}")

# 添加这个新函数来清理文件名中的非法字符
def clean_filename(filename):
    """移除文件名中的非法字符，替换为&"""
    # Windows文件名不允许的字符: < > : " / \ | ? *
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '&')
    # 额外移除文件名中的 ".."
    filename = filename.replace('..', '')
    return filename

while True:
    try:
        # 获取视频文件路径
        input_video = input("请输入视频文件完整路径 (输入'清理'移动处理过的文件，输入'退出'结束程序): ").strip('"')
        
        # 检查是否是退出命令
        if input_video.lower() in ['exit', 'q', '退出']:
            print("程序已退出")
            break
        
        # 检查是否是清理命令
        if input_video.lower() in ['clean', '清理','cl']:
            print("开始清理所有处理过的文件...")
            clean_processed_audio()  # 清理音频文件
            clean_processed_videos()  # 清理视频文件
            print("清理操作完成")
            continue
        
        if not os.path.isfile(input_video):
            print("无效的文件路径")
            continue
            
        # 检查文件是否为MP3格式
        is_mp3 = os.path.splitext(input_video.lower())[1] == '.mp3'
        
        # 获取并清理文件名中的非法字符
        file_dir = os.path.dirname(input_video)
        file_name = os.path.basename(input_video)
        clean_file_name = clean_filename(file_name)
        
        # 移动视频到视频目录
        video_name = clean_file_name  # 使用清理后的文件名
        if is_mp3:
            # 如果是MP3文件，直接使用原始文件路径
            input_audio = input_video
        else:
            # 如果是视频文件，移动到视频目录，使用清理后的文件名
            try:
                # 如果原文件名包含非法字符，先在原位置重命名
                if file_name != clean_file_name:
                    clean_path = os.path.join(file_dir, clean_file_name)
                    shutil.move(input_video, clean_path)
                    input_video = clean_path
                # 然后移动到视频目录
                shutil.move(input_video, os.path.join(video_dir, video_name))
                input_video = os.path.join(video_dir, video_name)
            except Exception as e:
                print(f"移动文件失败: {str(e)}")
                continue

        # 生成临时MP3路径
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        temp_mp3 = os.path.join(music_dir, f"temp_{timestamp}.mp3")

        # 获取音乐信息
        TIT2_name = input("输入音乐名称（中文/英文）: ").strip()
        # 清理音乐名称中的非法字符
        TIT2_name = clean_filename(TIT2_name)
        while True:
            date_prompt = f"输入时间（格式示例：2024.03.27或2024-03-27）[上次：{last_input_date if last_input_date else '无'}]: "
            input_date = input(date_prompt).strip()
            
            formatted_date = ""
            extra_text = ""
            
            # 如果用户直接回车且有历史记录，使用上次输入的日期
            if input_date == "" and last_input_date:
                input_date = last_input_date
                print(f"使用上次日期: {input_date}")
            
            # 处理输入的日期和文本
            date_result, text_part = validate_date(input_date)
            
            if date_result:
                # 有有效日期，保存当前输入的日期作为下次默认值
                formatted_date = date_result
                extra_text = clean_filename(text_part)  # 清理额外文本中的非法字符和".."
                # 仅保存格式化后的日期，不包含额外文本
                last_input_date = formatted_date
                break
            elif text_part and last_input_date:
                # 只有文本没有日期，但有上次日期，使用上次日期并将文本放在前面
                # last_input_date应该已经是纯日期格式，不需要再次验证
                formatted_date = last_input_date
                extra_text = clean_filename(text_part)  # 清理文本中的非法字符和".."
                print(f"使用上次日期并添加文本: {extra_text} {formatted_date}")
                break
            
            print("日期格式不正确，请重新输入")

        # 生成最终文件名，包含额外文本
        if extra_text:
            # 如果有额外文本，加入括号中
            final_name = f"{TIT2_name}（{extra_text} {formatted_date}）.mp3"
        else:
            # 没有额外文本，使用原始格式
            final_name = f"{TIT2_name}（{formatted_date}）.mp3"

        # 根据文件类型处理
        if is_mp3:
            # 如果是MP3文件，直接重命名
            final_path = os.path.join(music_dir, final_name)
            # 添加MP3元数据
            try:
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-i', input_audio,
                    '-c', 'copy',
                    '-map_metadata', '-1',
                    '-metadata', f'TPE1={TPE1_name}',
                    '-metadata', f'TALB={TALB_name}',
                    '-metadata', f'TIT2={TIT2_name}',
                    '-metadata', f'date={formatted_date}',
                    '-id3v2_version', '3',
                    temp_mp3
                ]
                subprocess.run(ffmpeg_cmd, check=True)
                # 删除原始复制的MP3文件
                #os.remove(input_audio)
                
                # 归档原始MP3文件到old_music_dir
                original_mp3_name = os.path.basename(input_video)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                clean_name = remove_timestamp(original_mp3_name)
                archive_name = f"{os.path.splitext(clean_name)[0]}_{timestamp}{os.path.splitext(original_mp3_name)[1]}"
                archive_path = os.path.join(old_music_dir, archive_name)
                
                print(f"正在归档原始MP3文件: {original_mp3_name}")
                shutil.move(input_video, archive_path)
                print(f"MP3文件已移至: {os.path.relpath(archive_path)}")
                
            except Exception as e:
                print(f"处理MP3元数据失败: {str(e)}")
                # 如果处理失败，至少重命名文件
                shutil.move(input_audio, final_path)
                
                # 尝试归档原始MP3文件
                try:
                    original_mp3_name = os.path.basename(input_video)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    clean_name = remove_timestamp(original_mp3_name)
                    archive_name = f"{os.path.splitext(clean_name)[0]}_{timestamp}{os.path.splitext(original_mp3_name)[1]}"
                    archive_path = os.path.join(old_music_dir, archive_name)
                    
                    print(f"正在归档原始MP3文件: {original_mp3_name}")
                    shutil.move(input_video, archive_path)
                    print(f"MP3文件已移至: {os.path.relpath(archive_path)}")
                except Exception as move_error:
                    print(f"归档原始MP3文件失败: {str(move_error)}")
        else:
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
            
        # 生成最终文件路径
        if not is_mp3:
            final_path = os.path.join(music_dir, final_name)

        # 移动文件并记录日志
        try:
            shutil.move(temp_mp3, final_path)
            
            # 清理当前处理过的视频文件
            try:
                # 只处理当前视频文件，而不是所有视频文件
                if not is_mp3 and os.path.exists(os.path.join(video_dir, video_name)):
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    # 清理文件名中的时间戳
                    clean_name = remove_timestamp(video_name)
                    new_name = f"{os.path.splitext(clean_name)[0]}_{timestamp}{os.path.splitext(video_name)[1]}"
                    dest_path = os.path.join(old_video_dir, new_name)
                    
                    print(f"正在归档视频文件: {video_name}")
                    shutil.move(os.path.join(video_dir, video_name), dest_path)
                    print(f"视频文件已移至: {os.path.relpath(dest_path)}")
                else:
                    print(f"视频文件 {video_name} 已不存在，可能已被移动")
                    # 尝试从旧目录中找到可能的文件名（用于日志记录）
                    possible_files = [f for f in os.listdir(old_video_dir) 
                                      if f.startswith(os.path.splitext(clean_name)[0])]
                    if possible_files:
                        new_name = possible_files[0]  # 使用第一个匹配的文件
                    else:
                        new_name = "未知"  # 如果找不到匹配的文件
            except Exception as e:
                print(f"视频文件归档失败: {str(e)}")
                new_name = video_name  # 如果移动失败，使用原始名称

            # 记录目录路径
            if is_mp3:
                # 如果是MP3文件，记录MP3归档信息
                log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 作者: {TPE1_name} | 专辑: {TALB_name} | 音乐文件: {final_name} | 原始MP3: {archive_name} -> {old_music_dir}\n"
            else:
                # 如果是视频文件，记录视频归档信息
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