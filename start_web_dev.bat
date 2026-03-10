@echo off
chcp 65001 >nul
echo ============================================================
echo 通达信选股系统 - Web 服务启动脚本（开发模式）
echo ============================================================
echo.

REM 设置开发模式（开启 DEBUG）
set FLASK_DEBUG=true
set FLASK_HOST=0.0.0.0
set FLASK_PORT=5000

echo 运行模式：开发模式 (DEBUG=开启)
echo 监听地址：http://%FLASK_HOST%:%FLASK_PORT%
echo.
echo 提示：开发模式下代码修改会自动重载
echo 按 Ctrl+C 停止服务
echo.
echo ============================================================
echo.

cd /d "%~dp0"
uv run python web/app.py
