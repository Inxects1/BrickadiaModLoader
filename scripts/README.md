# Build Scripts

This folder contains scripts for building and packaging the Brickadia Mod Loader.

## 📜 Scripts

### Build Scripts

- **[build_exe.bat](build_exe.bat)** - Windows batch file for building the executable
- **[build_exe.ps1](build_exe.ps1)** - PowerShell script for building the executable (recommended)
- **[BrickadiaModLoader.spec](BrickadiaModLoader.spec)** - PyInstaller specification file

### Utility Scripts

- **[make_transparent_icon.py](make_transparent_icon.py)** - Creates transparent icons from logo

## 🔨 How to Build

### Using PowerShell (Recommended)

```powershell
cd scripts
.\build_exe.ps1
```

### Using Batch File

```cmd
cd scripts
build_exe.bat
```

### Manual Build

```powershell
# From project root
python -m PyInstaller scripts\BrickadiaModLoader.spec
```

## 📦 Output

The build process creates:

- `dist/BrickadiaModLoader.exe` - The standalone executable
- `build/` - Temporary build files (can be deleted)

## ⚙️ Requirements

Make sure you have installed all dependencies:

```bash
pip install -r ../requirements.txt
```

## 🔧 Modifying the Build

Edit `BrickadiaModLoader.spec` to customize:

- Include additional files
- Change icon
- Modify build options
- Add hidden imports
