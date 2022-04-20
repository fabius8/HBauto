@echo off
for /l %%i in (41,1,50) do (
echo %%i
start "" /b /d .. HBweb.py %%i
choice /t 60 /d y /n >null
)
pause
