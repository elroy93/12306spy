@echo off
chcp 65001


:: 检查python环境, 如果没有安装python, 请先安装python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    powershell -command "Write-Host 'Python is not installed. Please install Python 3.7 or above.' -ForegroundColor Red"
    echo downloads from  :  https://www.python.org/downloads/
    pause
    exit /b
)
for /f "tokens=2 delims=." %%v in ('python --version 2^>^&1') do (
    set /a version=%%v
)

if %version% lss 7 (
    powershell -command "Write-Host 'Python version is below 3.7. Please install Python 3.7 or above' -ForegroundColor Red"
    echo downloads from  :  https://www.python.org/downloads/
    pause
    exit /b
)
echo Python is installed and meets the minimum version requirement.

:: 检查结束
python --version

powershell -command "Write-Host 'create virtual environment... ' -ForegroundColor Green"
python -m venv venv

powershell -command "Write-Host 'activating virtual environment... ' -ForegroundColor Green"
call .\venv\Scripts\activate.bat

:: 检查当前的虚拟环境
echo current path : %cd%

echo installing dependencies from requirements.txt...
:: 更新pip
python -m pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

powershell -command "Write-Host '--------------------------' -ForegroundColor Green"
powershell -command "Write-Host '     install success      ' -ForegroundColor Green"
powershell -command "Write-Host '--------------------------' -ForegroundColor Green"

:: 用jupyter notebook打开 main.ipynb

powershell -command "Write-Host 'start jupyter notebook' -ForegroundColor Green"
::jupyter notebook main.ipynb

python main.py

::打开浏览器 http://127.0.0.1:8000/
start http://127.0.0.1:8000

pause
:: 退出虚拟环境
deactivate
exit /b