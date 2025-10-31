# Build Script for Brickadia Mod Loader
# This script uses PyInstaller to create a standalone executable

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Brickadia Mod Loader - Build Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.7+ and try again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow

# Clean previous builds
if (Test-Path "build") {
    Remove-Item -Path "build" -Recurse -Force
    Write-Host "  ✓ Cleaned build folder" -ForegroundColor Gray
}
if (Test-Path "dist") {
    Remove-Item -Path "dist" -Recurse -Force
    Write-Host "  ✓ Cleaned dist folder" -ForegroundColor Gray
}
if (Test-Path "BrickadiaModLoader.spec") {
    Remove-Item -Path "BrickadiaModLoader.spec" -Force
    Write-Host "  ✓ Cleaned spec file" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Building executable with PyInstaller..." -ForegroundColor Cyan
Write-Host ""

# Build the executable
python -m PyInstaller --name="BrickadiaModLoader" `
    --onefile `
    --windowed `
    --hidden-import=tkinterdnd2 `
    --hidden-import=rarfile `
    --hidden-import=zipfile `
    --collect-all=tkinterdnd2 `
    main.py

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan

if (Test-Path "dist\BrickadiaModLoader.exe") {
    Write-Host ""
    Write-Host "✓ BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable created at:" -ForegroundColor Cyan
    Write-Host "  dist\BrickadiaModLoader.exe" -ForegroundColor White
    Write-Host ""
    
    $fileInfo = Get-Item "dist\BrickadiaModLoader.exe"
    $sizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
    Write-Host "File size: $sizeMB MB" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Test the executable by running it" -ForegroundColor White
    Write-Host "  2. Share 'BrickadiaModLoader.exe' with users" -ForegroundColor White
    Write-Host "  3. Include 'QUICKSTART.md' for instructions" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✗ BUILD FAILED!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the output above for errors." -ForegroundColor Yellow
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  - Missing dependencies (run: pip install -r requirements.txt)" -ForegroundColor White
    Write-Host "  - PyInstaller not installed (run: pip install pyinstaller)" -ForegroundColor White
    Write-Host ""
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
