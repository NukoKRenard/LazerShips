@echo off
pushd %~dp0

setlocal ENABLEDELAYEDEXPANSION

:retry
python main.py

if %ERRORLEVEL% NEQ 0 (
        echo An error occured when running the game.
        python --version > nul
        if !ERRORLEVEL! NEQ 0 (
            echo python is not installed. You can install python 3 from python.org or the microsoft store. Python is required for this game to work.
            echo We can redirect you to python.org. Press any key to visit the site...
            pause
            start https://python.org
            exit
        )
        for %%p in ("pyglm","pyopengl","pygame","numpy") do (
            python -c "import %%~p" > nul
            if !ERRORLEVEL! NEQ 0 (
                echo Python package %%p is not installed. To allow the game to work this package must be installed.
                echo To proceed with automatic installation, press Enter, you can also install manually using "pip install %%~p"
                pause
                echo installing %%p...
                pip install %%p
                echo %%p installed. Retrying...
            )
        )
        goto retry
)

