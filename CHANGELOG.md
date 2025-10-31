# Changelog

All notable changes to Brickadia Mod Loader will be documented in this file.

## [1.0.0] - 2025-10-31

### Added

- **Auto-Update Checker**: Automatically checks GitHub for new versions on startup
- **First-Time Setup Wizard**: Guides users through initial setup with auto-detection of Brickadia installation
- **Smart Installation Detection**: Automatically searches common installation paths for Brickadia
- **Version Display**: Shows current version in the UI
- Drag & drop support for .zip and .rar files
- Enable/disable mods with one click
- Visual mod management interface
- Automatic .pak file extraction from archives
- Safe mod storage (separate from game files)
- Persistent configuration system
- Settings panel for custom paths
- Multi-mod support

### Features

- 🎯 **Drag & Drop Interface** - Drop mod archives directly into the app
- 📦 **Archive Support** - Works with both .zip and .rar files
- ✅ **Toggle System** - Enable/disable mods instantly
- 🗂️ **Mod Management** - Track all installed mods and their status
- ⚙️ **Auto-Configuration** - Finds Brickadia automatically or guides you through setup
- 💾 **Safe Operations** - Mods stored separately, easy to backup
- 🔄 **Update Notifications** - Know when new versions are available
- 🎮 **User Friendly** - Clean, modern dark theme interface

### Technical

- Built with Python 3.14
- Uses tkinter for GUI
- tkinterdnd2 for drag & drop
- PyInstaller for standalone executable
- GitHub API integration for updates
- Windows Registry detection for Steam installations

### Known Issues

- RAR extraction requires WinRAR to be installed
- Some antivirus software may flag the executable (false positive)
- Windows SmartScreen may show warning on first run

---

## Future Plans

### Planned for 1.1.0

- Auto-update downloader (automatic exe replacement)
- Mod profiles (save/load mod configurations)
- Mod search and filter
- Mod categories/tags
- Export/import mod lists

### Planned for 1.2.0

- Mod conflict detection
- Mod load order management
- Backup/restore functionality
- Dark/light theme toggle
- Multi-language support

### Long-term Goals

- Cloud mod repository integration
- One-click mod installation from URLs
- Mod creator tools
- Automatic mod updates
- Cross-platform support (Linux, macOS)

---

**Note**: This is version 1.0.0 - the initial release. Please report any issues on the GitHub repository!
