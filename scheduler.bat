@echo off
echo DO NOT CLOSE THIS WINDOW
set CONDAPATH=C:\Users\yanis.schaerer\Anaconda3
set ENVNAME=sn_entsoe_data

if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

REM Close all open images (and suppress error message if no open image)
taskkill /f /im Microsoft.Photos.exe > nul 2> nul

REM Run python files
python %~dp0\core\import_data_entsoe.py
python %~dp0\core\generate_files.py

REM Open created image
for %%# in ("%~dp0\Export\Grafiken\01_Letzte30\DE\*.png") do set file_name="%%~nx#"
%~dp0\Export\Grafiken\01_Letzte30\DE\%file_name%

call conda deactivate

echo.
set wait_time=10
echo Press any button to continue or wait %wait_time% seconds

timeout /t %wait_time% > nul