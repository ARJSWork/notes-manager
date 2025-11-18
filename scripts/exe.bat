@echo off
setlocal

c:
cd \Data\home\Temp
cd
tar -xf \Data\home\Code\py\AgendaMaker.tar
cd notes-manager
cd
call run.bat
cd \Data\home\Temp
rmdir /s /q notes-manager 