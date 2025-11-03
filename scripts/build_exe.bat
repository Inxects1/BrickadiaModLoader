@echo off
echo Building Brickadia Mod Loader...
echo.

REM Change to project root directory
cd ..

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable using the spec file
pyinstaller scripts\BrickadiaModLoader.spec

echo.
echo Build complete! Check the 'dist' folder for BrickadiaModLoader.exe
echo.
pause
