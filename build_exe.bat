@echo off
echo Building Brickadia Mod Loader...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
pyinstaller --name="BrickadiaModLoader" ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --add-data="icon.ico;." ^
    --hidden-import=tkinterdnd2 ^
    --hidden-import=rarfile ^
    --hidden-import=zipfile ^
    --collect-all=tkinterdnd2 ^
    main.py

echo.
echo Build complete! Check the 'dist' folder for BrickadiaModLoader.exe
echo.
pause
