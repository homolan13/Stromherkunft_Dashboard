@echo off
REM Change coding to allow umlaute. ATTENTION: This file is saved with coding ANSI (codepage 1252) (and not with default UTF-8)!
chcp 1252 > nul

echo DO NOT CLOSE THIS WINDOW
set CONDAPATH=C:\Users\yanis.schaerer\Anaconda3
set ENVNAME=sn_entsoe_data
set DEST="H:\KKW Unterstützung\Kernanlagen (CH)\Produktionsdaten Entso-E CH"

if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

REM Close all open images (and suppress error message if no open image)
taskkill /f /im Microsoft.Photos.exe > nul 2> nul

REM Run python files
python %~dp0\core\import_data_entsoe.py
python %~dp0\core\generate_files.py

REM Copy all non-static directories and files from local computer to destination
robocopy %~dp0 %DEST% log.txt > nul
robocopy %~dp0\Export %DEST%\Export /mir > nul
robocopy %~dp0\core\generation %DEST%\core\generation /mir > nul
robocopy %~dp0\core\outages %DEST%\core\outages /mir > nul
echo.
echo Files copied to %DEST%

REM Open created image
::for %%# in ("%~dp0\Export\Grafiken\01_Letzte30\DE\*.png") do set FILE_NAME="%%~nx#"
::%~dp0\Export\Grafiken\01_Letzte30\DE\%FILE_NAME%

call conda deactivate

echo.
set WAIT_TIME=10
echo Press any button to continue or wait %WAIT_TIME% seconds

timeout /t %WAIT_TIME% > nul