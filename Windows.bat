@echo off
setlocal enabledelayedexpansion

rem --- Функція для перевірки наявності програми ---
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
    rem Скачування та установка Python, якщо він не встановлений
    rem Вказати тут шлях до інсталятору Python, якщо необхідно
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.9.0/python-3.9.0.exe -OutFile python_installer.exe"
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
) else (
    echo Python is already installed.
)

rem --- Оновлення pip ---
echo Upgrading pip...
python -m pip install --upgrade pip

rem --- Встановлення необхідних Python пакунків ---
echo Checking and installing/updating Python packages...
for %%p in (requests tqdm tabulate patool) do (
    python -c "import %%p" >nul 2>nul
    if errorlevel 1 (
        echo Installing %%p...
        python -m pip install %%p
    ) else (
        echo %%p is already installed. Updating...
        python -m pip install --upgrade %%p
    )
)

rem --- Встановлення unrar за допомогою Chocolatey (якщо доступно) ---
where unrar >nul 2>nul
if %errorlevel% neq 0 (
    echo unrar is not installed. Installing unrar...
    rem Перевірка наявності Chocolatey
    where choco >nul 2>nul
    if %errorlevel% neq 0 (
        echo Chocolatey is not installed. Installing Chocolatey...
        powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    )
    rem Встановлення unrar через Chocolatey
    choco install -y unrar
) else (
    echo unrar is already installed.
)

rem --- Встановлення bsdtar за допомогою Chocolatey ---
where bsdtar >nul 2>nul
if %errorlevel% neq 0 (
    echo bsdtar is not installed. Installing bsdtar...
    choco install -y bsdtar
) else (
    echo bsdtar is already installed.
)

rem --- Виконання основного Python скрипту ---
echo Running main.py...
python main.py

endlocal
pause
