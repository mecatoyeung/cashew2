@echo off
cmd /k ".\backend\.venv\Scripts\activate & python .\backend\manage.py runserver --noreload"
pause