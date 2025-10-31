# Brickadia Mod Loader

A simple and intuitive mod loader for Brickadia that allows you to easily install, enable, disable, and manage custom mods.

## Features

- 🎯 **Drag & Drop Support** - Simply drag .zip or .rar files into the application
- 📦 **Automatic Extraction** - Automatically extracts .pak files from archives
- ✅ **Enable/Disable Mods** - Toggle mods on and off with one click
- 🗂️ **Mod Management** - Keep all your mods organized in one place
- ⚙️ **Easy Configuration** - Set your Brickadia installation path once
- 💾 **Safe Storage** - Mods are stored separately and copied when enabled

## Download & Installation

### For Users (Easy Way)

1. **Download** the latest `BrickadiaModLoader.exe` from the releases
2. **Run** the executable - no installation needed!
3. That's it! The mod loader is ready to use.

**Note:** For RAR file support, you may need to install [WinRAR](https://www.win-rar.com/download.html) on your system.

### For Developers (Running from Source)

1. Make sure you have Python 3.7 or higher installed
2. Install the required dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the application:

```powershell
python main.py
```

### Building the Executable

To build your own executable:

```powershell
python -m PyInstaller --name="BrickadiaModLoader" --onefile --windowed --hidden-import=tkinterdnd2 --hidden-import=rarfile --hidden-import=zipfile --collect-all=tkinterdnd2 main.py
```

Or use the provided build script:

```powershell
.\build_exe.ps1
```

The executable will be created in the `dist` folder.

## Usage

2. **First Time Setup:**

   - Click the "⚙ Settings" button
   - Set the path to your Brickadia Paks folder (usually something like `C:\Program Files\Brickadia\Brickadia\Content\Paks`)
   - Set the path where you want to store your mods (default is in your home directory)
   - Click "Save Settings"

3. **Installing Mods:**

   - Drag and drop a .zip or .rar file containing .pak files into the drop zone
   - Or click "Browse for Archive" to select a file
   - The mod will be extracted and added to your mod list

4. **Managing Mods:**
   - **Enable**: Select a mod and click "Enable Mod" to activate it (copies to Brickadia folder)
   - **Disable**: Select a mod and click "Disable Mod" to deactivate it (removes from Brickadia folder)
   - **Delete**: Select a mod and click "Delete Mod" to permanently remove it

## How It Works

1. When you install a mod, the loader extracts any .pak files from the archive
2. These .pak files are stored in your custom mods folder
3. When you enable a mod, the .pak file is copied to your Brickadia Paks folder
4. When you disable a mod, the .pak file is removed from the Brickadia Paks folder (but kept in storage)
5. All mod states are tracked in a `mods.json` file

## Configuration Files

- `config.ini` - Stores your Brickadia installation path and mods storage location
- `mods.json` - Keeps track of all installed mods and their states

## Troubleshooting

**Q: The application won't start**

- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that you have Python 3.7+: `python --version`

**Q: RAR files won't extract**

- Install WinRAR or the unrar library
- Make sure WinRAR is in your system PATH

**Q: Mods aren't showing up in game**

- Make sure you've set the correct Brickadia Paks folder in Settings
- Verify that the mod is enabled (shows "✓ Enabled" in the status column)
- Restart Brickadia after enabling mods

**Q: Can't find Brickadia Paks folder**

- Look for: `<Brickadia Install Location>\Brickadia\Content\Paks`
- Common locations:
  - `C:\Program Files\Brickadia\Brickadia\Content\Paks`
  - `C:\Program Files (x86)\Steam\steamapps\common\Brickadia\Brickadia\Content\Paks`

## Requirements

- Python 3.7+
- tkinterdnd2 (for drag & drop)
- rarfile (for RAR extraction)
- WinRAR or UnRAR (for RAR support)

## License

This project is open source and available for anyone to use and modify.

## Disclaimer

This mod loader is an unofficial tool and is not affiliated with or endorsed by the Brickadia developers. Use at your own risk. Always backup your game files before using mods.
