@echo off
chcp 65001 >nul
echo ========================================
echo HERCU Admin 缓存清理工具
echo ========================================
echo.

echo 1. 关闭所有 HERCU Admin 进程...
taskkill /F /IM "HERCU Admin.exe" /T 2>nul
if %errorlevel%==0 (
    echo    ✓ 已关闭 HERCU Admin 进程
) else (
    echo    ℹ 未发现运行中的 HERCU Admin 进程
)
timeout /t 2 >nul

echo.
echo 2. 清理应用数据缓存...

set "app_data=%APPDATA%\hercu-admin"
set "local_app_data=%LOCALAPPDATA%\hercu-admin"

if exist "%app_data%\Session Storage" (
    rd /s /q "%app_data%\Session Storage" 2>nul
    echo    ✓ 已清理 Session Storage
)

if exist "%app_data%\Local Storage" (
    rd /s /q "%app_data%\Local Storage" 2>nul
    echo    ✓ 已清理 Local Storage
)

if exist "%app_data%\Cache" (
    rd /s /q "%app_data%\Cache" 2>nul
    echo    ✓ 已清理 Cache
)

if exist "%local_app_data%\Cache" (
    rd /s /q "%local_app_data%\Cache" 2>nul
    echo    ✓ 已清理 Local Cache
)

if exist "%app_data%\GPUCache" (
    rd /s /q "%app_data%\GPUCache" 2>nul
    echo    ✓ 已清理 GPU Cache
)

echo.
echo 3. 清理完成！
echo.
echo 现在可以重新启动 HERCU Admin 了
echo 应用将使用全新的缓存状态
echo.
echo ========================================
pause
