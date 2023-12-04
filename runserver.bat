@echo off
cmd /k ".\backend\.venv\Scripts\activate & python .\backend\manage.py runserver 0.0.0.0:8000 --noreload"
pause