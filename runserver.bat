@echo off
REM NET START "SQL Server (MSSQLSERVER)"
cmd /k "%~dp0\backend\.venv\Scripts\activate & python %~dp0\backend\manage.py runserver 0.0.0.0:8000 --noreload"
pause