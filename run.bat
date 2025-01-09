@echo off
pushd %~dp0

setlocal ENABLEDELAYEDEXPANSION

:retry
python main.py > log.txt

if %ERRORLEVEL% NEQ 0 (
        echo "\n" >> log.txt
        echo "ERROR DEBUG:" >> log.txt
        echo An error occured when running the game.
        python --version >> log.txt
        if !ERRORLEVEL! NEQ 0 (
            echo No python interpreter is installed on this computer. Please install the newest python version from python.org. Python is required for this game to work.
	    echo Please download the windows 64 bit installer. Please also make sure you enable the setting to add it to PATH.
	    echo To open python.org press any key...
            pause
            start https://www.python.org/downloads/windows/
            exit
        )

        for %%p in ("pyglm","pyopengl","pygame","numpy") do (

            if %%p EQU "pyglm" python -c "import glm" >> log.txt
            if %%p EQU "pyopengl" python -c "import OpenGL.GL" >> log.txt
            if %%p NEQ "pyglm" if %%p NEQ "pyopengl" python -c "import %%~p" >> log.txt

            if !ERRORLEVEL! NEQ 0 (
                echo Python package %%~p is not installed. To allow the game to work this package must be installed.
                echo To proceed with automatic installation, press Enter, you can also install manually using "pip install %%~p" or "python -m pip install %%~p"
                pause
                echo installing %%~p...
                python -m pip install %%~p >> log.txt
                echo %%p Testing installation...

                if %%p EQU "pyglm" python -c "import glm" >> log.txt
                if %%p EQU "pyopengl" python -c "import OpenGL.GL" >> log.txt
                if %%p NEQ "pyglm" if %%p NEQ "pyopengl" python -c "import %%~p" >> log.txt

                if !ERRORLEVEL! NEQ 0 (
                    echo Installation FAILED. Please install %%~p manually using "pip install %%~p" or "python -m pip install %%~p"
                    pause
                    exit
                )

                echo test passed.
            )
        )
        goto retry
)

