@echo off
setlocal

echo Cleaning up Gradio temporary directories...

REM Directory 1: C:\Users\<Current_User>\AppData\Local\Temp\gradio
set "DIR1=%LOCALAPPDATA%\Temp\gradio"
if exist "%DIR1%" (
    echo Cleaning %DIR1%...
    del /q /s "%DIR1%\*" >nul 2>&1
    for /d %%p in ("%DIR1%\*") do rmdir /q /s "%%p" >nul 2>&1
) else (
    echo Directory does not exist: %DIR1%
)

REM Directory 2: V:\ai\Irodori-TTS\gradio_outputs
set "DIR2=V:\ai\Irodori-TTS\gradio_outputs"
if exist "%DIR2%" (
    echo Cleaning %DIR2%...
    del /q /s "%DIR2%\*" >nul 2>&1
    for /d %%p in ("%DIR2%\*") do rmdir /q /s "%%p" >nul 2>&1
) else (
    echo Directory does not exist: %DIR2%
)

REM Directory 3: V:\ai\Irodori-TTS\gradio_outputs_voicedesign
set "DIR3=V:\ai\Irodori-TTS\gradio_outputs_voicedesign"
if exist "%DIR3%" (
    echo Cleaning %DIR3%...
    del /q /s "%DIR3%\*" >nul 2>&1
    for /d %%p in ("%DIR3%\*") do rmdir /q /s "%%p" >nul 2>&1
) else (
    echo Directory does not exist: %DIR3%
)

echo Cleanup completed!
endlocal
pause
