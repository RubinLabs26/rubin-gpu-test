@echo off
setlocal
python "%~dp0gpu_test.py" %*
if errorlevel 1 pause
