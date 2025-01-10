@echo off
cd %~dp0
call .\env\Scripts\activate.bat
py %~dp0\csp.py %*