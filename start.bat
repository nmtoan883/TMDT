@echo off
color 0A
title Khởi động Hệ thống TMDT Electro

echo ========================================================
echo        TOOL KHOI DONG DU AN TMDT 1-CLICK (AUTO)
echo ========================================================
echo.

echo [1/4] Kiem tra va cai dat thu vien (Neu chua co ban)...
pip install -r requirements.txt >nul 2>&1
echo Done!
echo.

echo [2/4] Kiem tra Co So Du Lieu (Database)...
python manage.py makemigrations
python manage.py migrate
echo Done!
echo.

echo [3/4] Khoi tao Admin va mat hang mau (Seed Data)...
python seed.py
echo Done!
echo.

echo [4/4] Moi thu Da San Sang! Dang bat May Chu (Server)...
echo Nhan Ctrl+C de tat server.
echo ========================================================
python manage.py runserver
