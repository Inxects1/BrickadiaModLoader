# Brickadia Mod Loader - Release Package

## 📦 What You've Built

A complete, standalone mod loader for Brickadia with the following features:

### ✨ Key Features

- Drag & drop .zip/.rar files to install mods
- Enable/disable mods with one click
- Visual mod management interface
- Automatic .pak file extraction
- Safe mod storage (mods stored separately from game)
- Persistent configuration
- No Python installation required for end users

### 📁 Files in This Project

#### **For Distribution** (Share with users):

- `dist/BrickadiaModLoader.exe` - **The main executable (11.72 MB)**
- `QUICKSTART.md` - Quick start guide for users
- `README.md` - Full documentation

#### **For Development**:

- `main.py` - Main application source code
- `requirements.txt` - Python dependencies
- `build_exe.ps1` - PowerShell build script
- `build_exe.bat` - Windows batch build script
- `.gitignore` - Git ignore rules

#### **Documentation**:

- `README.md` - Complete user documentation
- `QUICKSTART.md` - Quick start guide
- `DISTRIBUTION.md` - Distribution and sharing guide
- `RELEASE_INFO.md` - This file

### 🚀 How to Share Your Mod Loader

**Option 1: Simple File Sharing**

1. Share just the `BrickadiaModLoader.exe` file
2. Include `QUICKSTART.md` for instructions
3. Upload to Google Drive, Dropbox, or similar

**Option 2: GitHub Release (Recommended)**

1. Create a GitHub repository
2. Push your source code
3. Create a new Release
4. Attach `BrickadiaModLoader.exe` as a release asset
5. Copy the QUICKSTART.md content into the release notes

**Option 3: Itch.io**

1. Create an itch.io account
2. Upload as a free tool
3. Perfect for game mod communities!

### 💻 System Requirements

**For Users**:

- Windows 10/11
- ~15 MB free disk space
- Optional: WinRAR (for .rar file support)

**For Developers**:

- Python 3.7 or higher
- PyInstaller 6.16.0+
- tkinterdnd2 0.4.0+
- rarfile 4.2+

### 🔨 Rebuilding the Executable

If you make changes to `main.py`, rebuild with:

```powershell
python -m PyInstaller --name="BrickadiaModLoader" --onefile --windowed --hidden-import=tkinterdnd2 --hidden-import=rarfile --hidden-import=zipfile --collect-all=tkinterdnd2 main.py
```

Or use the build script:

```powershell
.\build_exe.ps1
```

The new executable will be in `dist/BrickadiaModLoader.exe`

### 📝 Version Information

**Build Date**: October 31, 2025
**Version**: 1.0.0

**Dependencies**:

- Python: 3.14.0
- PyInstaller: 6.16.0
- tkinterdnd2: 0.4.3
- rarfile: 4.2

### 🐛 Known Limitations

1. **RAR Support**: Requires WinRAR installed on user's system
2. **Antivirus**: May be flagged by some antivirus software (false positive)
3. **Windows Only**: Currently only supports Windows (cross-platform possible with modifications)

### 🔮 Future Enhancements (Ideas)

- Add mod version checking
- Support for mod dependencies
- Automatic mod updates
- Mod categories/tags
- Search and filter functionality
- Mod conflict detection
- Backup/restore functionality
- Custom mod installation order
- Mod profiles (enable/disable groups of mods)

### ⚖️ License & Legal

This mod loader is:

- ✅ Free and open source
- ✅ Unofficial (not affiliated with Brickadia)
- ✅ Provided "as-is" without warranty
- ✅ Use at your own risk

**Disclaimer**: Always backup your Brickadia installation before using mods or mod loaders.

### 📧 Support

**For Users**:

- Read the QUICKSTART.md for common questions
- Check README.md for detailed documentation

**For Developers**:

- Source code is well-commented
- All major functions have docstrings
- Feel free to modify and improve!

### 🎉 You're All Set!

Your mod loader is complete and ready to share. The executable in `dist/BrickadiaModLoader.exe` is a standalone file that anyone can download and run without installing Python or any dependencies.

**Next Steps**:

1. Test the executable on your system
2. Share it with your Brickadia community
3. Gather feedback and iterate
4. Consider adding the future enhancements listed above

Good luck with your mod loader! 🚀
