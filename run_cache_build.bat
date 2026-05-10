@echo off
REM Runner: calls cache_builder_v3.py repeatedly until all books are done
cd /d c:\projects\AI黑客松
set NO_PROXY=localhost,127.0.0.1,open.bigmodel.cn,huggingface.co

:loop
call venv\Scripts\python -u cache_builder_v3.py 2>&1
echo --- restarting in 2s ---
timeout /t 2 /nobreak >nul
goto loop
