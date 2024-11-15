@echo off
:begin
cd "%~dp0"

"venv/Scripts/python.exe" "main.py"
echo %ERRORLEVEL%
if %ERRORLEVEL% NEQ 0 (
    echo "Program error"
    echo "The program will now test to see if some packages arent installed. It will automatically install them if they aren't press ENTER to begin python package instillation"
    pause
    for %%p in ("pyopengl" "pyglm" "pygame" "numpy") do (
        "venv/Scripts/python.exe" -c "import %%p"
        if %ERRORLEVEL% NEQ 0 (
            venv\Scripts\python.exe -m pip install %%p
        )
    )
    goto begin
)

