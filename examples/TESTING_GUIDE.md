# Testing the UE4SS Support in Brickadia Mod Loader

## Quick Test Guide

I've created a test UE4SS mod for you to verify the new UE4SS support functionality.

### Test Files Location

- **Mod Folder**: `examples/TestUE4SSMod/`
- **Zip Archive**: `examples/TestUE4SSMod.zip` (ready to install)

### How to Test

1. **Prepare UE4SS** (if not already installed):

   - Download UE4SS from: https://github.com/UE4SS-RE/RE-UE4SS
   - Extract to `Brickadia/Binaries/Win64/`
   - Verify `UE4SS.dll` exists in that location

2. **Run the Mod Loader**:

   ```powershell
   python main.py
   ```

3. **Install the Test Mod**:

   - Click "Install Mod" button
   - Navigate to `examples/TestUE4SSMod.zip`
   - Select it and confirm

4. **Verify Detection**:

   - The mod loader should detect it as a UE4SS mod (Lua)
   - Check that it appears with `[UE4SS]` badge in the mod list
   - Description should say "UE4SS Mod (Lua)"

5. **Enable the Mod**:

   - Select the "Test UE4SS Mod" from the list
   - Click "Enable Mod"
   - It should install to `Brickadia/Binaries/Win64/Mods/TestUE4SSMod/`
   - If UE4SS.dll is not found, it should show a warning

6. **Verify Installation**:

   - Check that files exist at:
     - `Brickadia/Binaries/Win64/Mods/TestUE4SSMod/Scripts/main.lua`
     - `Brickadia/Binaries/Win64/Mods/TestUE4SSMod/Scripts/helper.lua`
     - `Brickadia/Binaries/Win64/Mods/TestUE4SSMod/enabled.txt`
   - Directory structure should be preserved

7. **Test in Game** (if you have Brickadia + UE4SS):
   - Launch Brickadia
   - Open UE4SS console (usually ~ key)
   - Look for "[Test UE4SS Mod]" messages
   - Should see initialization and periodic status messages

### What Should Work

✅ **Detection**: Mod loader identifies .lua files as UE4SS mod
✅ **Badge Display**: Shows `[UE4SS]` prefix in mod name
✅ **Installation**: Extracts to correct Mods folder
✅ **Structure**: Preserves Scripts/ subfolder structure
✅ **Metadata**: Reads modinfo.json correctly
✅ **Enable/Disable**: Can toggle mod on/off
✅ **UE4SS Check**: Warns if UE4SS.dll not present

### Testing Different Mod Types

You can also test with:

**Blueprint Mod** (create folder with):

- `Content/` folder with `.uasset` or `.umap` files
- Should detect as "UE4SS Mod (Blueprint)"

**C++ Mod** (create folder with):

- `.dll` files
- Should detect as "UE4SS Mod (C++)"

**Mixed Mod** (create folder with):

- `.lua` + `.uasset` files
- Should detect as "UE4SS Mod (Lua/Blueprint)"

### Expected Behavior

**On Install**:

- Success message: "Installed UE4SS mod: Test UE4SS Mod\nType: Lua"
- Note about UE4SS requirement

**On Enable**:

- If UE4SS.dll exists: Copies files and enables
- If UE4SS.dll missing: Shows warning with option to continue

**In Mod List**:

- Name: `[UE4SS] Test UE4SS Mod`
- Status: Shows enabled/disabled state
- Description: "A simple test mod for UE4SS that demonstrates Lua scripting"

### Troubleshooting

**Mod not detected as UE4SS?**

- Check that .lua files are present
- Verify no .pak files are in the archive

**Installation fails?**

- Check that Brickadia path is configured in Settings
- Verify you have write permissions

**Can't find installed files?**

- Look in `Brickadia/Binaries/Win64/Mods/TestUE4SSMod/`
- NOT in `Brickadia/Content/Paks/` (that's for PAK mods)

### Next Steps

After successful testing:

1. Test with a real UE4SS mod from the community
2. Test Blueprint and C++ mod detection
3. Test enable/disable multiple times
4. Test with both PAK and UE4SS mods installed simultaneously
