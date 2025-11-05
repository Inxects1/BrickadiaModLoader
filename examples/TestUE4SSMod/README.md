# Test UE4SS Mod

A simple example mod for testing the Brickadia Mod Loader's UE4SS support.

## Features

- Demonstrates basic Lua scripting with UE4SS
- Shows how to register hooks for game events
- Includes multiple Lua files to show code organization
- Provides logging examples for debugging

## Installation

1. Ensure UE4SS is installed in your Brickadia folder:

   - Download br_patcher.exe from: https://github.com/brickadia-community/br-lua-patcher/releases
   - Run it to patch Brickadia and install UE4SS (specifically compiled for Brickadia)
   - Or use the mod loader's automatic installation feature

2. Use the Brickadia Mod Loader to install this mod:

   - Create a zip file of this folder
   - Click "Install Mod" in the mod loader
   - Select the zip file

3. Enable the mod and launch Brickadia

## What It Does

When enabled, this mod will:

- Print initialization messages to the UE4SS console
- Hook into player controller events
- Log periodic status messages every 10 seconds
- Demonstrate helper function usage

## File Structure

```
TestUE4SSMod/
├── modinfo.json          # Mod metadata
├── enabled.txt           # UE4SS enabled flag
├── Scripts/
│   ├── main.lua         # Main mod script
│   └── helper.lua       # Helper functions
└── README.md            # This file
```

## Testing

After installation and enabling:

1. Launch Brickadia
2. Open the UE4SS console (usually ~ key)
3. Look for messages from "[Test UE4SS Mod]"
4. You should see initialization messages and periodic status updates

## Notes

- This is a minimal example for testing purposes
- Real mods can include Blueprint (.uasset), C++ (.dll), or mixed content
- The mod loader supports all UE4SS mod types
- `enabled.txt` with "1" tells UE4SS to load this mod

## Troubleshooting

**Mod not loading?**

- Verify UE4SS is installed correctly
- Check that the mod is enabled in the mod loader
- Look for error messages in the UE4SS console

**No console output?**

- Make sure UE4SS console is enabled in UE4SS settings
- Check UE4SS logs in `Brickadia/Binaries/Win64/`

## Creating Your Own Mod

Use this as a template:

1. Copy this folder structure
2. Modify `modinfo.json` with your mod details
3. Edit `Scripts/main.lua` with your custom code
4. Zip the folder and install via the mod loader
