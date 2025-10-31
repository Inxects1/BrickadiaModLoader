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

## For Mod Creators 🛠️

Want to make your mods look great in the mod loader? You can add custom metadata!

### Adding Custom Mod Information

Create a `modinfo.json` file in your mod archive alongside your .pak files:

```json
{
  "name": "My Awesome Mod",
  "description": "This mod adds cool new features to Brickadia!",
  "author": "YourName",
  "version": "1.0.0",
  "icon": "icon.png"
}
```

### Supported Fields

- **name**: Display name for your mod (shown in the mod list)
- **description**: Brief description of what your mod does
- **author**: Your name or username
- **version**: Version number (e.g., "1.0.0", "2.1.3")
- **icon**: Path to an icon image file (PNG recommended, will be displayed at 48x48 pixels)

### Icon Guidelines

- **Format**: PNG, JPG, or other common image formats
- **Size**: Any size (will be automatically resized to 48x48)
- **Recommended**: 256x256 or 512x512 for best quality
- **Location**: Include in the same archive as your .pak file

### Multi-File Mods

The mod loader automatically handles mods with multiple files! If your mod includes:

- `.pak` - Main mod file
- `.ucas` - Unreal Engine asset file
- `.utoc` - Unreal Engine table of contents
- `.sig` - Signature file
- `.ini` - Configuration file
- `.txt` - Documentation or readme

Just include them all in your archive with the same base name (e.g., `MyMod.pak`, `MyMod.ucas`, `MyMod.utoc`), and the mod loader will handle them all together when enabling/disabling.

### Example Mod Structure

```
MyAwesomeMod.zip
├── MyAwesomeMod.pak
├── MyAwesomeMod.ucas
├── MyAwesomeMod.utoc
├── MyAwesomeMod.sig
├── modinfo.json
└── icon.png
```

### Complete modinfo.json Example

```json
{
  "name": "Ultimate Build Tools",
  "description": "Adds 50+ new building tools and shortcuts for advanced builders",
  "author": "BuildMaster",
  "version": "2.3.1",
  "icon": "icon.png"
}
```

### Testing Your Mod

1. Create your mod archive (.zip or .rar)
2. Include all necessary files (.pak, .ucas, etc.)
3. Add your `modinfo.json` and icon
4. Test by dragging into the mod loader
5. Check that your icon and info display correctly

For more detailed information, see [MOD_CREATOR_GUIDE.md](MOD_CREATOR_GUIDE.md)

---

## How It Works

1. When you install a mod, the loader extracts any .pak files (and related files) from the archive
2. All mod files are stored together in a dedicated folder in your mods storage location
3. When you enable a mod, all its files are copied to your Brickadia Paks folder
4. When you disable a mod, all its files are removed from the Brickadia Paks folder (but kept in storage)
5. All mod states and metadata are tracked in a `mods.json` file

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
