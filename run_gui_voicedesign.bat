@echo off
cd /d %~dp0
if not exist ".venv" (
    echo .venv directory not found. Please run 'uv sync' first.
    pause
    exit /b
)
call .venv\Scripts\activate
python gradio_app_voicedesign.py --server-name 0.0.0.0 --server-port 7861
pause
