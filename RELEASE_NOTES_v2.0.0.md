# Brickadia Mod Loader v2.0.0 - Release Notes

**Release Date:** October 31, 2025

## 🎉 Major Feature Update

This release brings a comprehensive set of new features that significantly enhance the mod management experience!

---

## ✨ New Features

### 🚀 Quick Launch

- **Steam Integration**: Launch Brickadia directly from the mod loader
- Opens Steam library to Brickadia's page for quick game launching
- Avoids authentication issues by using proper Steam navigation
- Includes helpful prompts and fallback options

### 🔍 Search & Filter System

- **Real-time Search**: Search mods as you type by name, description, or author
- **Status Filter**: Filter mods by status (All/Enabled/Disabled)
- **Instant Results**: Live filtering updates the mod list immediately
- Clean and intuitive search interface with 🔍 icon

### ⚡ Batch Operations

- **Enable All Mods**: Enable all mods at once with a single click
- **Disable All Mods**: Disable all mods with one button
- **Confirmation Dialogs**: Prevents accidental bulk changes
- **Status Feedback**: Shows how many mods were affected

### 📋 Mod Profiles

- **Save Configurations**: Save your current mod setup as named profiles
- **Quick Load**: Switch between different mod configurations instantly
- **Profile Management**: Delete unwanted profiles
- **JSON Storage**: Profiles saved in `profiles.json` for easy backup
- Perfect for different gameplay scenarios or testing

### 🎮 Game Settings Editor

- **Direct Access**: Edit GameUserSettings.ini from the mod loader
- **Opens in Notepad**: Simple and familiar editing experience
- **Auto-detection**: Automatically finds your Brickadia config file
- **Helpful Errors**: Clear messages if settings file isn't found

---

## 🔧 Improvements

### UI Enhancements

- **Larger Window**: Increased to 1200x950 for better visibility
- **Improved Layout**: All buttons and features are now easily accessible
- **Better Organization**: New buttons section with clear separators
- **Minimum Size**: Set to 1100x900 to prevent UI cramping
- **Color-Coded Buttons**: Different colors for different action types

### Code Quality

- **Fixed Deprecation Warnings**: Updated `trace_variable()` to `trace_add()`
- **Better Error Handling**: More comprehensive exception handling
- **Cleaner Code Structure**: Improved organization and readability
- **Performance**: Optimized mod list filtering and updates

---

## 📦 What's Included

- `BrickadiaModLoader.exe` - Standalone executable (no Python required)
- All features from v1.0.0:
  - ✅ Drag & Drop installation (.zip, .rar, .7z, .pak files)
  - ✅ Enable/Disable individual mods with checkboxes
  - ✅ View mod details (name, author, description, version)
  - ✅ Uninstall mods with confirmation
  - ✅ Automatic modinfo.json parsing
  - ✅ Persistent mod states (remembers enabled/disabled mods)

---

## 🎯 How to Use New Features

### Quick Launch

1. Click the green "🚀 Launch Brickadia" button at the top
2. Confirm the launch dialog
3. Steam will open to Brickadia - click PLAY

### Search & Filter

1. Type in the search box to find mods by name, author, or description
2. Use the dropdown to filter by status (All/Enabled/Disabled)
3. Results update instantly as you type

### Batch Operations

1. Click "✓ Enable All" to enable all mods at once
2. Click "✗ Disable All" to disable all mods
3. Confirm the action in the dialog that appears

### Mod Profiles

1. Click "📋 Profiles" to open the profile manager
2. Set up your mods how you want them
3. Enter a profile name and click "Save Current Configuration"
4. Later, select a profile and click "Load Selected Profile"
5. Delete unwanted profiles with "Delete Selected Profile"

### Game Settings

1. Click "⚙️ Game Settings" to open GameUserSettings.ini
2. Edit your game settings in Notepad
3. Save and close when done

---

## 📋 System Requirements

- Windows 10/11
- Steam installed (for Quick Launch feature)
- Brickadia installed via Steam
- No Python installation required (standalone .exe)

---

## 🐛 Bug Fixes

- Fixed Steam launch authentication errors
- Fixed window size not showing all buttons
- Fixed trace_variable deprecation warning
- Improved executable path detection
- Better error messages for missing files

---

## 🔜 Coming Soon (Potential Future Features)

- Mod Load Order Management (drag & drop reordering)
- Mod Update Checker
- Mod Statistics Dashboard
- Backup & Restore System
- Mod Notes/Tags
- Online Repository Browser
- Conflict Detection
- Screenshots Gallery

---

## 💾 Installation

1. Download `BrickadiaModLoader.exe` from the releases page
2. Place it anywhere on your computer
3. Run the executable
4. Point it to your Brickadia Paks folder when prompted
5. Start managing your mods!

---

## 🙏 Feedback

Found a bug or have a feature request? Please open an issue on the GitHub repository!

---

## 📝 Changelog Summary

- Added Quick Launch with Steam integration
- Added real-time search and filter system
- Added batch enable/disable all operations
- Added mod profile save/load system
- Added game settings editor button
- Increased window size to 1200x950
- Fixed deprecation warnings
- Improved error handling
- Enhanced UI layout and organization
- Better Steam integration

---

**Enjoy the new features!** 🎮🧱
