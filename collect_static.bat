@echo off
chcp 65001 >nul
echo [收集] 開始收集靜態檔案...
python manage.py collectstatic --noinput

echo [完成] 靜態檔案收集完成!
echo [提示] 請重新啟動開發伺服器:
echo    python manage.py runserver
pause
