# Example Mod Package

This folder contains an example of how to package a mod with custom information.

## Files in this example:

1. **modinfo.json** - Contains mod metadata
2. **ExampleMod.pak** - A placeholder .pak file (in real use, this would be your actual mod)
3. **icon.png** - Mod icon (you would provide your own)

## How to use:

1. Create your actual .pak file
2. Create a modinfo.json with your mod's information
3. Optionally add an icon.png file
4. Zip all files together
5. Drag and drop into the Brickadia Mod Loader

## What the mod loader will show:

- **Name**: From modinfo.json "name" field
- **Description**: From modinfo.json "description" field  
- **Author**: From modinfo.json "author" field
- **Version**: From modinfo.json "version" field
- **Icon**: Your custom icon image

See MOD_CREATOR_GUIDE.md for full documentation!
