:begin
set pythonpath = "venv/Scripts/python.exe"
cd "%~dp0"
%pythonpath% "main.py"

if %ERRORLEVEL% NEQ 0 {
    echo "Program error"
    echo "Checking packages"
    set packages = "pyopengl" "pyglm" "pygame" "numpy"
    echo "Testing package installs..."
    for %%package in (%packages%) {
        %pythonpath% -c "import %%package"
        if %ERRORLEVEL% NEQ 0 {
            echo "Python package %%package not installed. Press enter to proceed with installation."
            echo "(this package is mandatory for the program to work)"
            pause
            %pythonpath% -m "pip install %%package"
            echo "Testing install..."
            %pythonpath% -c "import %%package"
            if %ERRORLEVEL% NEQ 0 goto packagerror
        }
    }
    goto begin
}

goto eof

:packageerror
echo "Error occured when installing packages. Please install them manually..."
pause
