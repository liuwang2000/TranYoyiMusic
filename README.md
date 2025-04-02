<div align="center">

# 🎵 TranYoyiMusic 视频音频提取与处理工具 🎵

<img src="https://github.com/liuwang2000/TranYoyiMusic/blob/main/Yoyi.png" alt="Yoyi" width="180"/>

![版本](https://img.shields.io/badge/版本-1.5.1-blue)
![许可证](https://img.shields.io/badge/许可证-MIT-yellow)
![Python](https://img.shields.io/badge/Python-3.8+-green)

</div>

## 📝 项目介绍

TranYoyiMusic 是一款专为音乐学习与整理设计的工具，可以轻松从视频中提取音频并进行管理。本工具支持从视频文件中提取音频、设置元数据（如作者、专辑、日期等）、剪辑音频片段，并自动整理归档文件。

## ✨ 主要功能

- **🎧 音频提取**：从视频文件中提取高质量MP3音频
- **📋 元数据设置**：为音频文件添加作者、专辑、标题、日期等信息
- **✂️ 音频剪辑**：精确剪辑音频的起止时间
- **🗃️ 自动归档**：处理完成的文件自动归档备份
- **📊 日志记录**：详细记录所有文件处理操作
- **🔄 便捷日期输入**：支持记忆上次日期，支持在日期中添加额外文本
- **🧹 全局清理**：一键清理所有处理过的视频和音频文件

## 🔧 环境要求

- 💻 Windows 操作系统
- 🐍 Python 3.8 或更高版本
- 🎞️ FFmpeg（通过安装脚本自动安装）

## 📥 安装方法

### 克隆或下载项目

1. 使用Git克隆项目（推荐）:
   ```
   git clone https://github.com/liuwang2000/TranYoyiMusic.git
   ```

2. 或直接下载ZIP包并解压到您想要的文件夹

### ⚠️ 初始设置
首次使用前，建议删除以下文件以获取全新设置体验：
- 删除 `config.ini`（如果存在）- 这将允许您设置自己的作者和专辑信息
- 删除 `directory.log`（如果存在）- 开始一个全新的操作日志

## 🚀 快速开始

### 🔍 安装 FFmpeg

- **自动安装**：双击运行 `install_ffmpeg.bat` 即可完成安装
  - 脚本会自动从GitHub下载FFmpeg并解压到项目目录中
  - 解压完成后即可使用，无需额外配置环境变量
  - ⚠️ 需下载约**92MB**文件，建议使用稳定网络
  - 🌐 从GitHub下载可能需要科学上网，如遇问题请使用手动安装方式
  - 📥 备用下载地址：[备份](https://github.com/liuwang2000/TranYoyiMusic/releases/download/v1.4/ffmpeg-2025-03-24-git-cbbc927a67-essentials_build.zip)

- **手动安装**：
  1. 从[GitHub官方](https://github.com/GyanD/codexffmpeg/releases/download/2025-03-24-git-cbbc927a67/ffmpeg-2025-03-24-git-cbbc927a67-essentials_build.zip)或[备份](https://github.com/liuwang2000/TranYoyiMusic/releases/download/v1.4/ffmpeg-2025-03-24-git-cbbc927a67-essentials_build.zip)下载FFmpeg压缩包
  2. 将下载的压缩包解压到项目根目录
  3. 确保解压后的文件夹名为`ffmpeg-2025-03-24-git-cbbc927a67-essentials_build`

### 📹 从视频提取音频

1. 双击运行 `starTran.bat` 或在命令行中执行 `python process_videos.py`
2. 根据提示输入视频文件路径（可直接拖放文件到窗口）
3. 输入音乐名称与日期信息
   - 支持直接回车使用上次输入的日期
   - 支持在日期前后添加额外文本，会一同显示在文件名中
4. 系统自动处理并保存MP3文件到music目录
5. 输入"清理"命令可手动归档所有处理过的视频和音频文件
6. 输入"退出"命令结束程序

### ✂️ 剪辑音频

1. 双击运行 `starTrim.bat` 或在命令行中执行 `python trim_audio.py`
2. 根据提示输入MP3文件路径（可直接拖放文件到窗口）
3. 输入剪辑起始和结束时间（支持秒数或分:秒格式）
4. 系统自动备份原文件并生成剪辑后的新文件

## 📖 使用详解

### 🔄 视频转音频工作流程

```
[视频文件] → 输入到程序 → 设置音乐名称与日期 → 生成MP3 → 原视频自动归档
```

### ✂️ 音频剪辑工作流程

```
[MP3文件] → 输入到程序 → 设置起止时间 → 生成剪辑后的MP3 → 原文件自动备份
```

### 📋 输入规范

1. **📹 视频文件**：支持MP4、AVI、MOV等常见格式
2. **🎵 音乐命名**：支持中英文混合，如"月光奏鸣曲"或"Moonlight_Sonata"
3. **📅 日期格式**：
   - 支持格式：2024.03.27、2024-03-27、2024年3月27日等
   - 系统自动标准化为8位数字（例：20240327）
   - 支持在日期前后添加额外文本（例：小提琴20240327、20240327第一课）
   - 直接按回车可使用上次输入的日期
   - 如只输入文本无日期，会使用上次输入的日期并添加文本
   - 自动处理文件名中的特殊字符和".."，确保生成有效文件名
4. **⏱️ 剪辑时间**：
   - 支持秒数（如：120）或分:秒格式（如：2:30）
   - 输入0表示不剪切该端点

### 📊 清理与归档功能

- **自动清理**：程序启动时会自动将music目录中的MP3文件移动到old目录
- **手动清理**：在主界面输入"清理"命令可手动归档所有处理过的视频和音频文件
- **自动去除时间戳**：系统会自动删除文件名中已有的时间戳，避免重复添加
- **简化信息显示**：清理过程中只显示必要的汇总信息，保持界面整洁

## 📂 目录结构

```
TranYoyiMusic/
├── videos/         # 待处理视频存放目录
│   └── old/        # 处理后视频归档目录
├── music/          # 生成的MP3文件目录
│   └── old/        # 历史音频备份目录
├── directory.log   # 操作日志记录
├── process_videos.py  # 视频处理主脚本
├── trim_audio.py      # 音频剪辑工具
├── starTran.bat       # 启动视频处理脚本
├── starTrim.bat       # 启动音频剪辑脚本
├── install_ffmpeg.bat # FFmpeg安装脚本
└── config.ini         # 配置文件（存储作者、专辑信息）
```

## ❓ 常见问题与解决方案

### 🚫 未检测到 FFmpeg
- 运行 `install_ffmpeg.bat` 自动安装
- 或按上述步骤手动配置环境变量
- 重启命令行窗口后再次尝试

### 📅 日期格式错误
- 确保输入格式如：2024.03.27、2024-03-27
- 系统会自动处理为标准格式

### ⏱️ 剪辑时间格式错误
- 检查时间格式是否为秒数（如120）或分:秒格式（如2:30）
- 确保起始时间小于结束时间
- 输入0表示不剪切该端点

### ❌ 文件处理失败
- 确保文件路径不包含特殊字符
- 检查磁盘剩余空间是否充足（建议>500MB）
- 确保文件未被其他程序占用

### 🔄 需要重新设置作者/专辑信息
- 删除项目根目录下的 `config.ini` 文件
- 重新运行程序，系统会提示您输入新的作者和专辑信息
- 这些信息将用于所有后续处理的音频文件

### 💼 如何批量管理已处理的文件
- 在主界面输入"清理"命令可手动归档当前所有音频文件
- 系统会自动移除文件名中重复的时间戳，保持命名整洁
- 所有文件会被移至 music/old 目录，便于集中管理
- 日志文件中会详细记录所有移动操作，方便追踪

## ⚠️ 使用注意事项

- 视频文件路径最好不要包含中文和特殊符号
- 处理过程中不要关闭命令行窗口
- 每次运行会自动将现有文件归档备份
- 所有操作都会记录在日志文件中

## 📝 更新日志

### v1.5.1
- 增强文件名处理功能，自动清除文件名中的".."字符
- 改进文件名安全性，确保生成合法有效的文件名
- 优化额外文本处理逻辑，增强用户输入的兼容性

### v1.5.0
- 增强日期输入功能，支持在日期中添加额外描述文本
- 添加一键回车使用上次日期的便捷功能
- 改进"清理"命令，支持同时清理视频和音频文件
- 优化文件名格式，支持更灵活的命名方式

### v1.4.1
- 添加FFmpeg安装的备用下载地址，解决网络问题
- 优化安装脚本，自动尝试备用地址下载
- 改进下载失败处理逻辑，提高安装成功率

### v1.4.0
- 添加"清理"和"退出"命令支持，方便操作
- 增加自动移除文件名中已有时间戳的功能
- 优化清理过程中的信息显示，更加简洁
- 改进异常处理，提高程序稳定性

### v1.3.0
- 更换使用体积更小的FFmpeg essentials版本(92MB)，减少下载流量
- 优化批处理文件中文显示问题

### v1.2.0
- 修复批处理文件中文显示问题
- 优化安装脚本显示，添加网络和文件大小提示

### v1.1.0
- 改进批处理文件，支持任意位置启动
- 增加项目克隆安装说明
- 更新安装脚本，简化FFmpeg安装流程

### v1.0.0
- 初始版本发布
- 支持从视频提取音频功能
- 支持音频剪辑功能
- 支持自动归档和日志记录

---

<div align="center">

### 使用步骤示意图

<img src="Yoyi.png" alt="Yoyi使用示例" width="250"/>

© 2025 TranYoyiMusic - 用❤️制作

</div>