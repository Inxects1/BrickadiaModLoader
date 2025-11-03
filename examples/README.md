# Examples

This folder contains example mods and templates to help you create your own Brickadia mods.

## 📁 Contents

### Example Mod

- **[example_mod/](example_mod/)** - A complete example mod folder structure
- **[example_mod.zip](example_mod.zip)** - Pre-packaged example mod ready to install

### Templates

- **[mod_template.json](mod_template.json)** - Template for modinfo.json file

## 🎮 Using the Example Mod

1. In the mod loader, click **"Install Mod"**
2. Select `example_mod.zip`
3. The mod will be installed with all metadata

## 📝 Creating Your Own Mod

Use the example mod as a reference for:

- Folder structure
- modinfo.json format
- Icon placement
- .pak file organization

For detailed instructions, see: [../docs/MOD_CREATOR_GUIDE.md](../docs/MOD_CREATOR_GUIDE.md)

## 📋 mod_template.json

This is a template for your `modinfo.json` file:

```json
{
  "name": "Your Mod Name",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "A brief description of your mod",
  "icon": "icon.png"
}
```

### Required Fields

- **name** - Display name for your mod

### Optional Fields

- **version** - Version number (e.g., "1.0.0")
- **author** - Your name or username
- **description** - What your mod does
- **icon** - Filename of your icon image (PNG recommended)

## 🔗 More Information

- [Mod Creator Guide](../docs/MOD_CREATOR_GUIDE.md)
- [Main README](../README.md)
