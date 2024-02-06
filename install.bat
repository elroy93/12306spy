@echo off
chcp 65001

echo Creating virtual environment...

python -m venv venv
echo Activating virtual environment...
call .\venv\Scripts\activate.bat


:: 检查当前的虚拟环境
echo %cd%

echo Installing dependencies from requirements.txt...
:: 更新pip
python -m pip install --upgrade pip
pip install -r requirements.txt

echo --------------------------
echo install success 
echo --------------------------


:: 用jupyter notebook打开 main.ipynb
jupyter notebook main.ipynb

pause

:: 退出虚拟环境
deactivate