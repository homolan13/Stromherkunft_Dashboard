@echo off
echo DO NOT CLOSE THIS WINDOW
set CONDAPATH=C:\Users\yanis.schaerer\Anaconda3
set ENVNAME=energy_prod

if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

python download_extract_save_remove.py
python visualization.py
python file_converter.py

call conda deactivate

echo.
echo Press any button to continue or wait 5 seconds

timeout /t 5 > nul