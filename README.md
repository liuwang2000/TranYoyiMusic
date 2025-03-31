# TranMusic 音频处理工具

[![GitHub release](https://img.shields.io/github/v/release/yourname/TranMusic)](https://github.com/yourname/TranMusic)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 本地运行
```bash
git clone https://github.com/yourname/TranMusic.git
cd TranMusic
python process_videos.py
```

## 环境要求
1. Windows 操作系统
2. Python 3.8+
3. FFmpeg环境（通过install_ffmpeg.bat安装或手动配置）

## 快速开始

### 1. 安装FFmpeg
双击运行 `install_ffmpeg.bat` 完成自动安装

**手动安装步骤**：
1. 访问 https://www.gyan.dev/ffmpeg/builds/ 下载完整版FFmpeg
2. 解压到`C:\Program Files\FFmpeg`
3. 右键【此电脑】→【属性】→【高级系统设置】→【环境变量】
4. 在Path变量中添加：`C:\Program Files\FFmpeg\bin`

### 2. 启动处理脚本
在命令行中执行：
```
python process_videos.py
```

## 详细使用说明

### 新增功能
1. 自动清理机制：每次运行自动将现有媒体文件归档至videos/old目录
2. 路径输入支持：可直接粘贴文件路径或拖放文件到PowerShell窗口
3. 日志追踪：音乐目录变更记录存储于music/directory.log
4. 音频剪辑功能：支持精确到秒的起止时间剪辑，自动备份原始文件至music/old目录

### 操作流程图
```
[现有MP3] → 自动归档至music/old
[视频文件] → 拖放至脚本 → 输入音乐名称 → 输入日期 → 生成新MP3
```

### 输入规范
1. 视频文件格式支持：
   - MP4/AVI/MOV 等常见格式
   - 建议分辨率≥720p

2. 音乐命名规则：
   - 支持中英文混合
   - 示例："月光奏鸣曲" 或 "Moonlight_Sonata"

3. 日期格式处理：
   - 支持多种输入格式：2024.03.27/2024-03-27/2024年3月27日
   - 自动标准化处理：移除所有非数字字符后格式化为8位数字（示例：20240327）
   - 错误格式将提示重新输入

4. 剪辑时间格式：
   - 支持秒数（如：120）或分:秒格式（如：2:30）
   - 起始时间需小于结束时间
   - 输入0表示不剪切开头/结尾

## 目录结构
```
TranMusic/
├── videos/         # 原始视频存放
│   └── old/       # 历史视频存档
├── music/         # 生成音乐文件
│   ├── old/       # 历史音乐存档
│   └── directory.log  # 目录变更记录
├── process_videos.py    # Python主脚本
├── trim_audio.py       # 音频裁剪工具
└── install_ffmpeg.bat  # 环境安装脚本
```

## 注意事项
❗ 文件处理完成后会自动执行：
1. 源视频移动至videos/old
2. 临时音频文件自动删除
3. 目录变更记录追加时间戳

## 常见问题
❓ 提示"未检测到FFmpeg"
✅ 解决方案：
1. 运行 install_ffmpeg.bat 完成自动安装
2. 或按上述手动配置环境变量
3. 重启命令行窗口

❓ Python脚本运行报错
✅ 解决方案：
1. 确认Python版本≥3.8
2. 检查文件路径是否包含中文字符
3. 确保视频文件未被其他程序占用

❓ 日期输入报错
✅ 正确示例：
- 2024年3月27日 → 输入 2024.03.27
- 2024/3/27 → 输入 2024-03-27

❓ 剪辑时间格式错误
✅ 解决方案：
1. 检查时间格式是否符合秒数（120）或分:秒（2:30）格式
2. 确保起始时间小于结束时间
3. 输入0表示不剪切该端点

❓ 剪辑后文件未生成
✅ 解决方案：
1. 检查music/old目录是否存在原始文件备份
2. 确认磁盘剩余空间＞500MB
3. 确保文件路径不含特殊符号

## 注意事项
⚠ 操作前请确保：
1. 视频文件路径不要包含中文符号
2. 保证磁盘剩余空间＞2GB
3. 处理过程中不要关闭CMD窗口

---
🔄 更新日志：
- 2024.03.27 初始版本发布