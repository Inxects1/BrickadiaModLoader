# 📦 Mod Creator Template

This template helps you package your Brickadia mods with custom information!

## 🎯 Quick Start

### Basic Mod Structure

Your mod archive (.zip or .rar) should contain:

```
MyMod.zip
├── YourMod.pak          # Your actual mod file (required)
└── modinfo.json         # Mod information (optional)
└── icon.png             # Mod icon (optional)
```

## 📝 modinfo.json Template

Create a file named `modinfo.json` in your mod archive with this content:

```json
{
  "name": "My Awesome Mod",
  "description": "This mod adds cool features to Brickadia!",
  "author": "YourName",
  "version": "1.0.0",
  "icon": "icon.png"
}
```

### Fields Explained:

- **name** (required): Display name of your mod
- **description** (optional): What your mod does
- **author** (optional): Your name or username
- **version** (optional): Mod version (e.g., "1.0.0")
- **icon** (optional): Filename of the icon image (must be in the same archive)

## 🖼️ Adding an Icon

1. Create a square PNG image (recommended: 256x256 pixels)
2. Name it `icon.png` (or whatever you specify in modinfo.json)
3. Include it in your mod archive

## 📦 Example Mod Package

**MyAwesomeMod.zip contains:**

```
MyAwesomeMod.zip
├── MyAwesomeMod.pak
├── modinfo.json
└── icon.png
```

**modinfo.json:**

```json
{
  "name": "Super Building Tools",
  "description": "Adds advanced building tools and shortcuts to make building faster and easier!",
  "author": "BuilderPro",
  "version": "2.1.0",
  "icon": "icon.png"
}
```

## ✅ Tips

- Keep the modinfo.json simple and small
- Use a clear, descriptive name
- Icon should be square (same width and height)
- The .pak file is still required - modinfo.json just adds extra info
- If no modinfo.json is provided, the mod loader will use the .pak filename as the mod name

## 🚀 Testing Your Mod Package

1. Create your modinfo.json file
2. Add an icon.png (optional)
3. Put them in a .zip file with your .pak file
4. Drag and drop into the Brickadia Mod Loader
5. Check if your custom name and description appear!

## 📋 Common Mistakes

❌ **Don't do this:**

- Naming the file "mod.json" instead of "modinfo.json"
- Forgetting to include the actual .pak file
- Using a non-square icon image

✅ **Do this:**

- Name it exactly "modinfo.json"
- Always include your .pak file
- Keep descriptions short and clear
- Use PNG format for icons

## 🎨 Icon Guidelines

**Recommended specs:**

- Format: PNG with transparency
- Size: 256x256 pixels (or any square size)
- File size: Under 1MB
- Style: Clear and recognizable when small

## 📚 Full Example

Here's a complete, real-world example:

**Package:** TerrainEnhancer.zip

**Contents:**

```
TerrainEnhancer.zip
├── TerrainEnhancer-UE4.pak
├── modinfo.json
└── terrain_icon.png
```

**modinfo.json:**

```json
{
  "name": "Terrain Enhancer Pro",
  "description": "Adds realistic terrain textures and improved ground materials with HD quality.",
  "author": "TerrainMaster",
  "version": "3.2.1",
  "icon": "terrain_icon.png"
}
```

When installed, the mod loader will show:

- ✅ Custom name: "Terrain Enhancer Pro"
- ✅ Description in details
- ✅ Author credit
- ✅ Version number
- ✅ Custom icon thumbnail

---

**Need help?** Open an issue on the GitHub repository!

**Want to share your mod?** Include modinfo.json to make it look professional! 🎉
