@echo off
chcp 65001 >nul

echo ========================================================
echo                FFmpeg 自动安装程序
echo ========================================================
echo ' 提示:'
echo ' - 将下载约170MB的文件，请确保网络畅通'
echo ' - 下载可能需要科学上网，如遇下载失败请尝试手动下载'
echo ' - 完整下载链接:'
echo   https://github.com/GyanD/codexffmpeg/releases/download/2025-03-24-git-cbbc927a67/ffmpeg-2025-03-24-git-cbbc927a67-full_build.zip
echo ========================================================
echo.

set /p confirm=是否继续安装？(Y/N): 
if /i "%confirm%" NEQ "Y" goto :End

echo 正在下载FFmpeg，请耐心等待...
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/GyanD/codexffmpeg/releases/download/2025-03-24-git-cbbc927a67/ffmpeg-2025-03-24-git-cbbc927a67-full_build.zip' -OutFile 'ffmpeg_temp.zip'}"
if %ERRORLEVEL% neq 0 (
    echo 下载FFmpeg失败，请检查网络连接或手动下载
    echo 请访问以下链接手动下载:
    echo   https://github.com/GyanD/codexffmpeg/releases/download/2025-03-24-git-cbbc927a67/ffmpeg-2025-03-24-git-cbbc927a67-full_build.zip
    goto End
)

echo 正在解压FFmpeg...
powershell -Command "& {Expand-Archive -Path 'ffmpeg_temp.zip' -DestinationPath '.' -Force}"
if %ERRORLEVEL% neq 0 (
    echo 解压FFmpeg失败
    goto End
)

echo 清理临时文件...
del ffmpeg_temp.zip
if exist ffmpeg-2025-03-24-git-cbbc927a67-full_build (
    echo FFmpeg安装成功！
    echo 现在您可以直接使用TranMusic工具了
) else (
    echo FFmpeg安装失败，请手动下载并解压
)

:End
echo.
echo 按任意键退出...
pause >nul