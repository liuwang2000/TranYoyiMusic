@echo off
winget install -e --id Gyan.FFmpeg
if %ERRORLEVEL% equ 0 (
    echo FFmpeg安装成功！
) else (
    echo FFmpeg安装失败，请手动安装
)
pause