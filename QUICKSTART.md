# 🎮 Brickadia Mod Loader - Quick Start

## For End Users

### Installation (Super Easy!)

1. Download `BrickadiaModLoader.exe`
2. Put it anywhere you want (Desktop, Documents, etc.)
3. Double-click to run - **NO INSTALLATION NEEDED!**

### First Time Setup (30 seconds)

1. When the app opens, click **⚙ Settings** (top-right)
2. Click **Browse** next to "Brickadia Paks Folder"
3. Navigate to your Brickadia installation and find the Paks folder:
   - Example: `C:\Program Files\Brickadia\Brickadia\Content\Paks`
   - Or: `C:\Program Files (x86)\Steam\steamapps\common\Brickadia\Brickadia\Content\Paks`
4. Click **Save Settings**

### Using the Mod Loader

#### To Install a Mod:

1. Get a mod file (.zip or .rar containing .pak files)
2. **Drag and drop** it into the gray box in the app
   - OR click "Browse for Archive" to select it
3. The mod appears in your list!

#### To Enable a Mod:

1. Click on the mod in the list
2. Click **Enable Mod** button
3. Done! (Restart Brickadia to see changes)

#### To Disable a Mod:

1. Click on the mod in the list
2. Click **Disable Mod** button
3. Done! (Restart Brickadia)

#### To Delete a Mod:

1. Click on the mod in the list
2. Click **Delete Mod** button
3. Confirm deletion

### Tips

- ✅ Mods show **"✓ Enabled"** when active
- ❌ Mods show **"✗ Disabled"** when inactive
- 💾 Your mods are safely stored even when disabled
- 🔄 Always restart Brickadia after enabling/disabling mods
- 📦 You can enable/disable as many mods as you want

### Troubleshooting

**Windows says "Windows protected your PC"**

- This is normal for new executables
- Click "More info" → "Run anyway"

**Mods don't work in game**

- Make sure the mod is enabled (✓ Enabled)
- Check that you set the correct Brickadia Paks folder
- Restart Brickadia completely

**Can't extract .rar files**

- Install WinRAR from: https://www.win-rar.com/download.html
- .zip files work without any extra software

**Where are my mods stored?**

- Default: `C:\Users\YourName\BrickadiaModLoader\Mods`
- You can change this in Settings

### File Locations

The mod loader creates two files in the same folder as the .exe:

- `config.ini` - Your settings (folder paths)
- `mods.json` - List of installed mods

You can delete these to reset the app to defaults.

---

## For Developers

### Building from Source

1. Install Python 3.7+
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Run from source:

   ```powershell
   python main.py
   ```

4. Build executable:

   ```powershell
   python -m PyInstaller --name="BrickadiaModLoader" --onefile --windowed --hidden-import=tkinterdnd2 --hidden-import=rarfile --hidden-import=zipfile --collect-all=tkinterdnd2 main.py
   ```

   Or use the build script:

   ```powershell
   .\build_exe.ps1
   ```

### Project Structure

```
Brickadia Mod Loader/
├── main.py                 # Main application code
├── requirements.txt        # Python dependencies
├── build_exe.ps1          # PowerShell build script
├── build_exe.bat          # Batch build script
├── README.md              # Full documentation
├── DISTRIBUTION.md        # Distribution guide
├── QUICKSTART.md          # This file
├── .gitignore            # Git ignore rules
└── dist/
    └── BrickadiaModLoader.exe  # Built executable
```

### Technologies Used

- **Python 3.14** - Core language
- **tkinter** - GUI framework (built into Python)
- **tkinterdnd2** - Drag & drop support
- **rarfile** - RAR extraction
- **zipfile** - ZIP extraction (built into Python)
- **PyInstaller** - Executable creation

---

## Need Help?

For issues, questions, or suggestions:

- Check the README.md for detailed documentation
- Review the DISTRIBUTION.md for sharing information
- Open an issue on the project repository

---

**Enjoy your mods!** 🎉
