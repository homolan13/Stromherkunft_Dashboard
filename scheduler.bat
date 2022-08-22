@echo off
echo DO NOT CLOSE THIS WINDOW
set CONDAPATH=C:\Users\yanis.schaerer\Anaconda3
set ENVNAME=energy_prod

if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

python %~dp0\core\import_data_entsoe.py
python %~dp0\core\generate_files.py

call conda deactivate

echo.
set wait_time=10
echo Press any button to continue or wait %wait_time% seconds

timeout /t %wait_time% > nul