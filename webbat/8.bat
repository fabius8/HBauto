@echo off
for /l %%i in (71,1,80) do (
echo %%i
start "" /b /d .. HBweb.py %%i
choice /t 60 /d y /n >null
)
pause
