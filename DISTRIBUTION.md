# Distribution Guide for Brickadia Mod Loader

## What to Share

When distributing your mod loader to other users, you only need to share:

### Essential File:

- `dist/BrickadiaModLoader.exe` - The standalone executable (~12 MB)

### Optional Files:

- `README.md` - Instructions for users
- A copy of this distribution guide

## What Users Need

Users **DO NOT** need:

- ❌ Python installed
- ❌ Any dependencies or packages
- ❌ Any source code files

Users **MAY** need (for RAR support):

- ⚠️ WinRAR installed (if they want to extract .rar files)
- Most .zip files will work without any additional software

## How to Distribute

### Option 1: Direct Download

1. Upload `BrickadiaModLoader.exe` to a file hosting service:
   - GitHub Releases (recommended)
   - Google Drive
   - Dropbox
   - Your own website

### Option 2: GitHub Release

1. Create a new repository on GitHub
2. Upload your source code
3. Create a new Release
4. Attach `BrickadiaModLoader.exe` as a release asset
5. Include the README.md in the release notes

### Option 3: Itch.io

1. Create a free account on itch.io
2. Upload `BrickadiaModLoader.exe` as a downloadable file
3. Perfect for game mods and tools!

## First-Time User Instructions

Share these instructions with your users:

---

### Getting Started with Brickadia Mod Loader

1. **Download** `BrickadiaModLoader.exe`
2. **Run** the executable (double-click it)
3. If Windows shows a warning, click "More info" → "Run anyway" (this is normal for new executables)
4. On first launch:

   - Click the **⚙ Settings** button
   - Browse to your Brickadia Paks folder:
     - Usually: `C:\Program Files\Brickadia\Brickadia\Content\Paks`
     - Or: `C:\Program Files (x86)\Steam\steamapps\common\Brickadia\Brickadia\Content\Paks`
   - Click **Save Settings**

5. **Install mods:**

   - Drag and drop a .zip or .rar file into the application
   - Or click "Browse for Archive"

6. **Enable/Disable mods:**
   - Select a mod from the list
   - Click "Enable Mod" or "Disable Mod"
   - Restart Brickadia to see changes

---

## File Size

- Executable: ~12 MB
- Includes all necessary Python libraries
- No additional files needed

## Security Notes

Some antivirus software may flag PyInstaller executables as suspicious. This is a false positive because:

- PyInstaller packages Python code into an executable
- The executable is self-extracting
- Some AVs are cautious about self-extracting files

To resolve:

1. Add an exception in your antivirus for the executable
2. Build from source if you prefer
3. Submit the file to your antivirus vendor for whitelisting

## Testing Before Distribution

Before sharing with others, test:

1. ✅ Run the .exe on a clean Windows machine (without Python)
2. ✅ Test drag & drop with .zip files
3. ✅ Test drag & drop with .rar files (if WinRAR is installed)
4. ✅ Test enable/disable functionality
5. ✅ Test settings persistence (close and reopen)
6. ✅ Test with actual Brickadia game

## Support & Updates

When distributing, consider:

- Creating a GitHub repository for issues and updates
- Providing a contact method for bug reports
- Versioning your releases (e.g., v1.0, v1.1, etc.)
- Including a changelog for updates

## Legal Considerations

Remember to include:

- A disclaimer that this is unofficial and not affiliated with Brickadia
- A note that users should backup their game files
- Your license terms (if any)
- Credit to any libraries used (Python, tkinter, etc.)

## Version Information

Current version details:

- Python: 3.14.0
- PyInstaller: 6.16.0
- tkinterdnd2: 0.4.3
- rarfile: 4.2

Built on: October 31, 2025
