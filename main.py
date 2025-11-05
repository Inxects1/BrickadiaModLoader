import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import json
import shutil
import zipfile
import rarfile
from pathlib import Path
from tkinterdnd2 import DND_FILES, TkinterDnD
import configparser
import urllib.request
import webbrowser
import subprocess
import sys
import tempfile

# Tooltip class for hover tooltips
class ToolTip:
    """Create a tooltip for a given widget"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """Display the tooltip"""
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#2d2d2d", foreground="#ffffff",
                        relief=tk.SOLID, borderwidth=1,
                        font=("Segoe UI", 9), padx=8, pady=6)
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Hide the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# Set up WinRAR path for rarfile
def setup_winrar():
    """Find and set WinRAR executable path"""
    possible_paths = [
        r"C:\Program Files\WinRAR\UnRAR.exe",
        r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
        r"C:\Program Files\WinRAR\Rar.exe",
        r"C:\Program Files (x86)\WinRAR\Rar.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            rarfile.UNRAR_TOOL = path
            return True
    
    # Check if unrar is in PATH
    try:
        subprocess.run(['unrar'], capture_output=True)
        return True
    except:
        pass
    
    return False

# Try to set up WinRAR on module load
setup_winrar()


class BrickadiaModLoader:
    VERSION = "3.2.0"
    GITHUB_REPO = "Inxects1/BrickadiaModLoader"
    
    # Theme Colors
    THEME_BG_DARK = "#1e1e1e"      # Main background
    THEME_BG_PANEL = "#252525"      # Panel backgrounds
    THEME_BG_CARD = "#2d2d2d"       # Cards/frames
    THEME_ACCENT = "#5DADE2"        # Primary accent color (Brickadia blue)
    THEME_ACCENT_HOVER = "#4A9FD6"  # Accent hover state
    THEME_TEXT = "#ffffff"          # Main text
    THEME_TEXT_DIM = "#888888"      # Dimmed text
    THEME_SUCCESS = "#4CAF50"       # Success/enable
    THEME_WARNING = "#FF9800"       # Warning/disable
    THEME_DANGER = "#f44336"        # Danger/delete
    THEME_PURPLE = "#9C27B0"        # Special actions
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"Brickadia Mod Loader v{self.VERSION}")
        self.root.minsize(1300, 950)
        self.root.configure(bg=self.THEME_BG_DARK)
        
        # Load config first to get window position
        # Temporarily use root location for initial config load
        self.config_file = "config.ini"
        self.load_config()
        
        # Now move config and mods.json to mods storage folder
        self.setup_data_files()
        
        # Set window geometry from saved position or default
        if 'Window' in self.config and self.config['Window'].get('geometry'):
            self.root.geometry(self.config['Window']['geometry'])
        else:
            self.root.geometry("1400x1000")
        
        # Save window position on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize drag and drop data
        self.drag_data = {"index": None, "item": None}
        
        # Load and set window icon
        try:
            from PIL import Image, ImageTk
            # Get the correct path for the logo (works for both script and exe)
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                application_path = sys._MEIPASS
                logo_path = Path(application_path) / "logo.png"
            else:
                # Running as script
                application_path = os.path.dirname(os.path.abspath(__file__))
                logo_path = Path(application_path) / "assets" / "logo.png"
            if logo_path.exists():
                # Load logo for window icon (taskbar)
                logo_img = Image.open(logo_path)
                # Remove white background by making it transparent
                if logo_img.mode == 'RGB':
                    logo_img = logo_img.convert('RGBA')
                # Make white pixels transparent
                datas = logo_img.getdata()
                newData = []
                for item in datas:
                    # If pixel is white (or close to white), make it transparent
                    if item[0] > 240 and item[1] > 240 and item[2] > 240:
                        newData.append((255, 255, 255, 0))
                    else:
                        newData.append(item)
                logo_img.putdata(newData)
                
                # Set as window icon
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                self.root.iconphoto(True, self.logo_photo)
                
                # Create smaller version for UI (32x32)
                self.logo_ui = logo_img.resize((32, 32), Image.Resampling.LANCZOS)
                self.logo_ui_photo = ImageTk.PhotoImage(self.logo_ui)
            else:
                self.logo_ui_photo = None
        except Exception as e:
            print(f"Failed to load logo: {e}")
            self.logo_ui_photo = None
        
        # First time setup (before showing main window)
        if not self.config['Paths']['brickadia_paks']:
            # Hide main window during setup
            self.root.withdraw()
            self.first_time_setup()
            # Show main window after setup completes
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        
        # Check for updates (after setup, on every launch)
        self.check_for_updates()
        
        # Mod storage
        self.mods = self.load_mods()
        
        # Create GUI
        self.create_widgets()
        self.refresh_mod_list()
        
    def load_config(self):
        """Load configuration from file or create default"""
        self.config = configparser.ConfigParser()
        
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            # Default configuration
            self.config['Paths'] = {
                'brickadia_paks': '',
                'mods_storage': str(Path.home() / 'BrickadiaModLoader' / 'Mods')
            }
            self.config['Window'] = {
                'geometry': '1400x1000'
            }
            self.save_config()
        
        # Ensure Window section exists
        if 'Window' not in self.config:
            self.config['Window'] = {
                'geometry': '1400x1000'
            }
        
        # Create mods storage directory if it doesn't exist
        self.mods_storage_path = self.config['Paths']['mods_storage']
        os.makedirs(self.mods_storage_path, exist_ok=True)
    
    def setup_data_files(self):
        """Move config and mods data files to mods storage folder"""
        # Define new paths in mods storage folder
        new_config_file = Path(self.mods_storage_path) / "config.ini"
        new_mods_file = Path(self.mods_storage_path) / "mods.json"
        
        # Migrate old config file if it exists in root
        old_config = Path("config.ini")
        if old_config.exists() and not new_config_file.exists():
            try:
                import shutil
                shutil.copy(old_config, new_config_file)
                print(f"Migrated config.ini to {new_config_file}")
            except Exception as e:
                print(f"Could not migrate config: {e}")
        
        # Migrate old mods.json if it exists in root
        old_mods = Path("mods.json")
        if old_mods.exists() and not new_mods_file.exists():
            try:
                import shutil
                shutil.copy(old_mods, new_mods_file)
                print(f"Migrated mods.json to {new_mods_file}")
            except Exception as e:
                print(f"Could not migrate mods.json: {e}")
        
        # Update file paths to use new locations
        self.config_file = str(new_config_file)
        self.mods_data_file = str(new_mods_file)
        
        # Reload config from new location
        if new_config_file.exists():
            self.config.read(self.config_file)
        else:
            # Save config to new location
            self.save_config()
        
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def on_closing(self):
        """Handle window closing - save position and exit"""
        # Save window geometry
        self.config['Window']['geometry'] = self.root.geometry()
        self.save_config()
        self.root.destroy()
    
    def check_for_updates(self):
        """Check GitHub for new version"""
        try:
            url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'BrickadiaModLoader')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data['tag_name'].lstrip('v')
                
                if latest_version != self.VERSION:
                    result = messagebox.askyesno(
                        "Update Available",
                        f"A new version is available!\n\n"
                        f"Current version: {self.VERSION}\n"
                        f"Latest version: {latest_version}\n\n"
                        f"Would you like to download the update?",
                        icon='info'
                    )
                    
                    if result:
                        webbrowser.open(f"https://github.com/{self.GITHUB_REPO}/releases/latest")
                        messagebox.showinfo(
                            "Update Instructions",
                            "Download the new BrickadiaModLoader.exe from the releases page.\n\n"
                            "Replace your current exe with the new one.\n\n"
                            "Your mods and settings will be preserved!"
                        )
        except Exception as e:
            # Silently fail if update check fails (no internet, etc.)
            pass
    
    def find_brickadia_installation(self):
        """Try to automatically find Brickadia installation"""
        possible_paths = [
            Path("C:/Program Files/Brickadia"),
            Path("C:/Program Files (x86)/Brickadia"),
            Path("C:/Program Files/Steam/steamapps/common/Brickadia"),
            Path("C:/Program Files (x86)/Steam/steamapps/common/Brickadia"),
            Path.home() / "AppData" / "Local" / "Brickadia",
        ]
        
        # Check registry for Steam installation and all library folders
        try:
            import winreg
            
            # Get main Steam path
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
            steam_path = Path(steam_path.replace('/', '\\'))
            
            # Add main Steam library
            possible_paths.append(steam_path / "steamapps" / "common" / "Brickadia")
            
            # Parse libraryfolders.vdf to find all Steam library locations
            library_vdf = steam_path / "steamapps" / "libraryfolders.vdf"
            if library_vdf.exists():
                try:
                    with open(library_vdf, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Look for path entries in the VDF file
                        import re
                        # Match "path" entries
                        paths = re.findall(r'"path"\s+"([^"]+)"', content)
                        for lib_path in paths:
                            lib_path = Path(lib_path.replace('\\\\', '\\'))
                            possible_paths.append(lib_path / "steamapps" / "common" / "Brickadia")
                except:
                    pass
        except:
            pass
        
        # Check all possible paths
        for base_path in possible_paths:
            pak_path = base_path / "Brickadia" / "Content" / "Paks"
            if pak_path.exists() and pak_path.is_dir():
                return str(pak_path)
        
        return None
    
    def first_time_setup(self):
        """First time setup wizard"""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Welcome to Brickadia Mod Loader")
        setup_window.geometry("650x550")
        setup_window.configure(bg=self.THEME_BG_DARK)
        setup_window.transient(self.root)
        setup_window.grab_set()
        
        # Make it modal and prevent closing
        setup_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Center the window immediately
        setup_window.update_idletasks()
        x = (setup_window.winfo_screenwidth() // 2) - (setup_window.winfo_width() // 2)
        y = (setup_window.winfo_screenheight() // 2) - (setup_window.winfo_height() // 2)
        setup_window.geometry(f"650x550+{x}+{y}")
        
        # Bring to front
        setup_window.lift()
        setup_window.focus_force()
        
        # Title
        tk.Label(
            setup_window,
            text="🎮 Welcome to Brickadia Mod Loader!",
            font=("Arial", 18, "bold"),
            bg="#2b2b2b",
            fg="#ffffff"
        ).pack(pady=20)
        
        tk.Label(
            setup_window,
            text="Let's set up your Brickadia installation",
            font=("Arial", 12),
            bg="#2b2b2b",
            fg="#aaaaaa"
        ).pack(pady=5)
        
        # Auto-detect
        tk.Label(
            setup_window,
            text="Step 1: Locate Brickadia",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#ffffff"
        ).pack(pady=(30, 10))
        
        auto_detected = self.find_brickadia_installation()
        
        detection_label = None
        if auto_detected:
            detection_label = tk.Label(
                setup_window,
                text="✓ Brickadia installation detected!",
                font=("Arial", 11),
                bg="#2b2b2b",
                fg="#00ff00"
            )
            detection_label.pack(pady=5)
            
            tk.Label(
                setup_window,
                text=auto_detected,
                font=("Arial", 9),
                bg="#2b2b2b",
                fg="#888888",
                wraplength=500
            ).pack(pady=5)
        else:
            detection_label = tk.Label(
                setup_window,
                text="⚠ Could not auto-detect Brickadia",
                font=("Arial", 11),
                bg="#2b2b2b",
                fg="#ffaa00"
            )
            detection_label.pack(pady=5)
        
        tk.Label(
            setup_window,
            text="Select your Brickadia installation folder:",
            font=("Arial", 10),
            bg="#2b2b2b",
            fg="#aaaaaa"
        ).pack(pady=(20, 5))
        
        # Path selection
        path_frame = tk.Frame(setup_window, bg="#2b2b2b")
        path_frame.pack(pady=10, padx=40, fill=tk.X)
        
        path_var = tk.StringVar(value=auto_detected if auto_detected else "")
        path_entry = tk.Entry(
            path_frame,
            textvariable=path_var,
            font=("Arial", 10),
            state='readonly',
            readonlybackground="#3c3c3c",
            fg="#ffffff",
            disabledforeground="#ffffff",
            disabledbackground="#3c3c3c",
            insertbackground="#ffffff"
        )
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def browse_installation():
            folder = filedialog.askdirectory(
                title="Select Brickadia Installation Folder",
                initialdir="C:/Program Files"
            )
            if folder:
                # Look for Paks folder inside the selected directory
                folder_path = Path(folder)
                pak_path = None
                
                # Try multiple possible structures
                possible_structures = [
                    folder_path / "Brickadia" / "Content" / "Paks",
                    folder_path / "Content" / "Paks",
                    folder_path / "Paks",
                ]
                
                for possible_path in possible_structures:
                    if possible_path.exists() and possible_path.is_dir():
                        # Verify it's actually a Paks folder by checking for typical Unreal Engine files
                        pak_files = list(possible_path.glob("*.pak"))
                        if pak_files or possible_path.name == "Paks":
                            pak_path = possible_path
                            break
                
                if pak_path:
                    path_var.set(str(pak_path))
                    # Update status and enable continue button
                    status_label.config(text="✓ Valid Brickadia installation found!", fg="#00ff00")
                    continue_btn.config(state='normal', bg="#00aa00", fg="#ffffff")
                else:
                    path_var.set("")
                    status_label.config(text="✗ Invalid folder - Paks folder not found", fg="#ff0000")
                    continue_btn.config(state='disabled', bg="#555555", fg="#888888")
                    messagebox.showerror(
                        "Invalid Folder",
                        f"Could not find Brickadia Paks folder in:\n{folder}\n\n"
                        "Please select the main Brickadia installation folder.\n\n"
                        "Looking for structure like:\n"
                        "  Brickadia/Brickadia/Content/Paks\n"
                        "  or Brickadia/Content/Paks"
                    )
        
        tk.Button(
            path_frame,
            text="Browse...",
            command=browse_installation,
            bg="#0066cc",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT)
        
        tk.Label(
            setup_window,
            text="Tip: Select the main Brickadia folder, we'll find the Paks folder automatically!",
            font=("Arial", 9, "italic"),
            bg="#2b2b2b",
            fg="#888888"
        ).pack(pady=10)
        
        # Status label
        status_label = tk.Label(
            setup_window,
            text="",
            font=("Arial", 10, "bold"),
            bg="#2b2b2b",
            fg="#00ff00"
        )
        status_label.pack(pady=5)
        
        # Continue button (initially disabled)
        continue_btn = tk.Button(
            setup_window,
            text="Continue",
            state='disabled',
            bg="#555555",
            fg="#888888",
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=40,
            pady=10
        )
        
        # Continue button logic
        def continue_setup():
            selected_path = path_var.get()
            
            if not selected_path:
                messagebox.showerror(
                    "No Path Selected",
                    "Please select your Brickadia installation folder first!\n\n"
                    "Click 'Browse...' to locate Brickadia."
                )
                return
            
            # Validate the path exists
            if not Path(selected_path).exists():
                messagebox.showerror(
                    "Invalid Path",
                    "The selected path does not exist!\n\n"
                    "Please select a valid Brickadia installation folder."
                )
                return
            
            # Save configuration
            self.config['Paths']['brickadia_paks'] = selected_path
            self.save_config()
            
            # Close setup window
            setup_window.grab_release()
            setup_window.destroy()
            
            # Show success message
            self.root.after(100, lambda: messagebox.showinfo(
                "✓ Setup Complete!",
                f"Brickadia Mod Loader is ready to use!\n\n"
                f"Paks folder: {selected_path}\n\n"
                "You can now drag & drop mod files to install them."
            ))
        
        continue_btn.config(command=continue_setup)
        continue_btn.pack(pady=30)
        
        # Enable continue button if auto-detected
        if auto_detected:
            status_label.config(text="✓ Ready to continue!", fg="#00ff00")
            continue_btn.config(state='normal', bg="#00aa00", fg="#ffffff")
    
    def load_mods(self):
        """Load mods data from JSON file"""
        if os.path.exists(self.mods_data_file):
            with open(self.mods_data_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_mods(self):
        """Save mods data to JSON file"""
        with open(self.mods_data_file, 'w') as f:
            json.dump(self.mods, f, indent=4)
    
    def create_widgets(self):
        """Create the GUI widgets with modern layout"""
        # ===== TOP BAR =====
        top_bar = tk.Frame(self.root, bg=self.THEME_BG_PANEL, height=70)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)
        
        # Title section (left) with logo
        title_section = tk.Frame(top_bar, bg=self.THEME_BG_PANEL)
        title_section.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Create horizontal layout for logo and text
        title_inner = tk.Frame(title_section, bg=self.THEME_BG_PANEL)
        title_inner.pack(anchor="w")
        
        # Logo on the left
        if hasattr(self, 'logo_ui_photo') and self.logo_ui_photo:
            logo_label = tk.Label(
                title_inner,
                image=self.logo_ui_photo,
                bg=self.THEME_BG_PANEL
            )
            logo_label.pack(side=tk.LEFT, padx=(0, 12))
        
        # Text on the right
        text_frame = tk.Frame(title_inner, bg=self.THEME_BG_PANEL)
        text_frame.pack(side=tk.LEFT)
        
        title_label = tk.Label(
            text_frame, 
            text="Brickadia Mod Loader", 
            font=("Segoe UI", 18, "bold"),
            bg=self.THEME_BG_PANEL,
            fg=self.THEME_TEXT
        )
        title_label.pack(anchor="w")
        
        version_label = tk.Label(
            text_frame,
            text=f"v{self.VERSION}",
            font=("Segoe UI", 9),
            bg=self.THEME_BG_PANEL,
            fg=self.THEME_TEXT_DIM
        )
        version_label.pack(anchor="w")
        
        # Action buttons (right side of top bar)
        actions_frame = tk.Frame(top_bar, bg=self.THEME_BG_PANEL)
        actions_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Launch button (prominent)
        launch_btn = tk.Button(
            actions_frame,
            text="🚀 Launch Game",
            command=self.launch_brickadia,
            bg=self.THEME_ACCENT,
            fg=self.THEME_TEXT,
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=25,
            pady=12,
            cursor="hand2",
            activebackground=self.THEME_ACCENT_HOVER
        )
        launch_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(launch_btn, "Launch Brickadia via Steam")
        
        # Uninstall UE4SS button
        uninstall_ue4ss_btn = tk.Button(
            actions_frame,
            text="Uninstall UE4SS",
            command=self.uninstall_ue4ss,
            bg="#3a3a3a",
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=12,
            cursor="hand2",
            activebackground="#4a4a4a"
        )
        uninstall_ue4ss_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(uninstall_ue4ss_btn, "Remove UE4SS from Brickadia")
        
        # Settings button
        settings_btn = tk.Button(
            actions_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            bg="#3a3a3a",
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=12,
            cursor="hand2",
            activebackground="#4a4a4a"
        )
        settings_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(settings_btn, "Configure mod loader settings")
        
        # Game Settings button
        game_settings_btn = tk.Button(
            actions_frame,
            text="🎮 Game Settings",
            command=self.open_game_settings,
            bg="#3a3a3a",
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=12,
            cursor="hand2",
            activebackground="#4a4a4a"
        )
        game_settings_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(game_settings_btn, "Edit GameUserSettings.ini")
        
        # Open Paks Folder button
        paks_folder_btn = tk.Button(
            actions_frame,
            text="📁 Paks Folder",
            command=self.open_paks_folder,
            bg="#3a3a3a",
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=12,
            cursor="hand2",
            activebackground="#4a4a4a"
        )
        paks_folder_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(paks_folder_btn, "Open Brickadia Paks folder")
        
        # About button
        about_btn = tk.Button(
            actions_frame,
            text="ℹ️ About",
            command=self.open_about,
            bg="#3a3a3a",
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=12,
            cursor="hand2",
            activebackground="#4a4a4a"
        )
        about_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(about_btn, "View on GitHub")
        
        # Check Duplicates button
        check_dupes_btn = tk.Button(
            actions_frame,
            text="🔍 Check Duplicates",
            command=self.check_for_duplicates,
            bg="#3a3a3a",
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=12,
            cursor="hand2",
            activebackground="#4a4a4a"
        )
        check_dupes_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(check_dupes_btn, "Check for duplicate mods")
        
        # ===== MAIN CONTENT AREA =====
        main_content = tk.Frame(self.root, bg=self.THEME_BG_DARK)
        main_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left side - Mod Library (wider)
        left_panel = tk.Frame(main_content, bg=self.THEME_BG_DARK)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Drop zone (compact, modern design)
        drop_frame = tk.Frame(left_panel, bg=self.THEME_BG_CARD, relief=tk.FLAT, bd=0, highlightthickness=2, highlightbackground="#3a3a3a")
        drop_frame.pack(fill=tk.X, pady=(0, 15))
        
        drop_inner = tk.Frame(drop_frame, bg=self.THEME_BG_CARD)
        drop_inner.pack(padx=20, pady=15)
        
        tk.Label(
            drop_inner,
            text="📦",
            font=("Segoe UI", 24),
            bg=self.THEME_BG_CARD,
            fg=self.THEME_TEXT
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        drop_text_frame = tk.Frame(drop_inner, bg=self.THEME_BG_CARD)
        drop_text_frame.pack(side=tk.LEFT)
        
        self.drop_label = tk.Label(
            drop_text_frame,
            text="Drop mod files here to install",
            font=("Segoe UI", 12, "bold"),
            bg=self.THEME_BG_CARD,
            fg=self.THEME_TEXT
        )
        self.drop_label.pack(anchor="w")
        
        tk.Label(
            drop_text_frame,
            text="Supports .zip, .rar, .7z, and .pak files",
            font=("Segoe UI", 9),
            bg=self.THEME_BG_CARD,
            fg=self.THEME_TEXT_DIM
        ).pack(anchor="w")
        
        # Browse button
        browse_btn = tk.Button(
            drop_inner,
            text="📁 Browse",
            command=self.browse_archive,
            bg=self.THEME_ACCENT,
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            activebackground=self.THEME_ACCENT_HOVER
        )
        browse_btn.pack(side=tk.LEFT, padx=(15, 0))
        
        # Enable drag and drop
        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        
        # Mod library header with search
        library_header = tk.Frame(left_panel, bg=self.THEME_BG_PANEL, height=50)
        library_header.pack(fill=tk.X, pady=(0, 10))
        library_header.pack_propagate(False)
        
        # Left side - title and count
        header_left = tk.Frame(library_header, bg=self.THEME_BG_PANEL)
        header_left.pack(side=tk.LEFT, padx=15, pady=10)
        
        list_label = tk.Label(
            header_left,
            text="📚 Mod Library",
            font=("Segoe UI", 14, "bold"),
            bg=self.THEME_BG_PANEL,
            fg=self.THEME_TEXT
        )
        list_label.pack(side=tk.LEFT)
        
        self.mod_count_label = tk.Label(
            header_left,
            text="(0 mods)",
            font=("Segoe UI", 10),
            bg=self.THEME_BG_PANEL,
            fg=self.THEME_TEXT_DIM
        )
        self.mod_count_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Right side - search and filter
        header_right = tk.Frame(library_header, bg=self.THEME_BG_PANEL)
        header_right.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Filter dropdown
        self.filter_var = tk.StringVar(value="All Mods")
        filter_style = ttk.Style()
        filter_style.configure("TCombobox", fieldbackground="#3a3a3a", background="#3a3a3a", foreground="#ffffff")
        
        filter_menu = ttk.Combobox(
            header_right,
            textvariable=self.filter_var,
            values=["All Mods", "Enabled Only", "Disabled Only"],
            state="readonly",
            width=13,
            font=("Segoe UI", 9)
        )
        filter_menu.pack(side=tk.RIGHT, padx=(10, 0))
        filter_menu.bind('<<ComboboxSelected>>', lambda e: self.filter_mods())
        
        # Search entry
        search_frame = tk.Frame(header_right, bg="#3a3a3a", relief=tk.FLAT)
        search_frame.pack(side=tk.RIGHT)
        
        tk.Label(
            search_frame,
            text="🔍",
            font=("Segoe UI", 10),
            bg="#3a3a3a",
            fg="#888888"
        ).pack(side=tk.LEFT, padx=(8, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *args: self.filter_mods())
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            bg="#3a3a3a",
            fg="#ffffff",
            insertbackground="#ffffff",
            bd=0,
            width=25,
            relief=tk.FLAT
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 8), pady=6)
        
        # Mod list (treeview)
        tree_frame = tk.Frame(left_panel, bg="#2d2d2d")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure modern style for treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("ModTree.Treeview",
                       background="#2d2d2d",
                       foreground="#ffffff",
                       rowheight=60,
                       fieldbackground="#2d2d2d",
                       borderwidth=0,
                       relief=tk.FLAT)
        style.configure("ModTree.Treeview.Heading",
                       background="#252525",
                       foreground="#ffffff",
                       borderwidth=0,
                       relief=tk.FLAT,
                       font=("Segoe UI", 10, "bold"))
        style.map('ModTree.Treeview',
                 background=[('selected', self.THEME_ACCENT)],
                 foreground=[('selected', self.THEME_TEXT)])
        
        self.mod_tree = ttk.Treeview(
            tree_frame,
            columns=("Name", "Status", "Info"),
            show="tree headings",
            style="ModTree.Treeview",
            yscrollcommand=scrollbar.set
        )
        
        self.mod_tree.heading("#0", text="")
        self.mod_tree.heading("Name", text="Mod Name")
        self.mod_tree.heading("Status", text="Status")
        self.mod_tree.heading("Info", text="Details")
        
        self.mod_tree.column("#0", width=70, stretch=False)
        self.mod_tree.column("Name", width=300)
        self.mod_tree.column("Status", width=100)
        self.mod_tree.column("Info", width=380)
        
        self.mod_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar.config(command=self.mod_tree.yview)
        
        # Add right-click context menu
        # On Windows, Button-3 is right-click
        def on_right_click(event):
            print("RIGHT CLICK DETECTED!")
            self.show_context_menu(event)
        
        self.mod_tree.bind("<Button-3>", on_right_click)
        
        # Store for icon images (prevent garbage collection)
        self.mod_icons = {}
        
        # Right side - Mod Load Order
        right_panel = tk.Frame(main_content, bg=self.THEME_BG_PANEL, width=280)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Load order header
        order_header = tk.Frame(right_panel, bg=self.THEME_BG_PANEL)
        order_header.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            order_header,
            text="🔢 Load Order",
            font=("Segoe UI", 12, "bold"),
            bg=self.THEME_BG_PANEL,
            fg=self.THEME_TEXT
        ).pack(anchor="w")
        
        tk.Label(
            order_header,
            text="Drag mods to reorder",
            font=("Segoe UI", 9),
            bg=self.THEME_BG_PANEL,
            fg=self.THEME_TEXT_DIM
        ).pack(anchor="w")
        
        # Load order list with Canvas for custom rendering
        order_frame = tk.Frame(right_panel, bg=self.THEME_BG_CARD)
        order_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        order_scroll = ttk.Scrollbar(order_frame)
        order_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas for custom load order items with icons
        self.order_canvas = tk.Canvas(
            order_frame,
            bg=self.THEME_BG_CARD,
            bd=0,
            highlightthickness=0,
            yscrollcommand=order_scroll.set
        )
        self.order_canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        order_scroll.config(command=self.order_canvas.yview)
        
        # Frame inside canvas to hold mod items
        self.order_inner_frame = tk.Frame(self.order_canvas, bg=self.THEME_BG_CARD)
        self.order_canvas_window = self.order_canvas.create_window(0, 0, anchor='nw', window=self.order_inner_frame)
        
        # Bind to update scrollregion and canvas width
        self.order_inner_frame.bind('<Configure>', lambda e: self.order_canvas.configure(scrollregion=self.order_canvas.bbox("all")))
        self.order_canvas.bind('<Configure>', lambda e: self.order_canvas.itemconfig(self.order_canvas_window, width=e.width))
        
        # Store references for drag and drop
        self.order_items = []  # List of frame widgets
        self.drag_data = {"index": None, "item": None, "start_y": None}
        
        # Store load order icon cache
        self.load_order_icons = {}
        
        # Order control buttons
        order_btn_frame = tk.Frame(right_panel, bg=self.THEME_BG_PANEL)
        order_btn_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        tk.Button(
            order_btn_frame,
            text="▲ Move Up",
            command=self.move_mod_up,
            bg="#3a3a3a",
            fg="#ffffff",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#4a4a4a"
        ).pack(fill=tk.X, pady=2)
        
        tk.Button(
            order_btn_frame,
            text="▼ Move Down",
            command=self.move_mod_down,
            bg="#3a3a3a",
            fg="#ffffff",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#4a4a4a"
        ).pack(fill=tk.X, pady=2)
        
        # ===== BOTTOM BAR - Action Buttons =====
        bottom_bar = tk.Frame(self.root, bg=self.THEME_BG_PANEL, height=65)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)
        bottom_bar.pack_propagate(False)
        
        btn_frame = tk.Frame(bottom_bar, bg=self.THEME_BG_PANEL)
        btn_frame.pack(pady=12)
        
        # Mod actions
        tk.Label(
            btn_frame,
            text="Selected Mod:",
            font=("Segoe UI", 9, "bold"),
            bg=self.THEME_BG_PANEL,
            fg=self.THEME_TEXT_DIM
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="✓ Enable",
            command=self.enable_selected_mod,
            bg=self.THEME_SUCCESS,
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            activebackground="#45a049"
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            btn_frame,
            text="✗ Disable",
            command=self.disable_selected_mod,
            bg=self.THEME_WARNING,
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            activebackground="#e68900"
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            btn_frame,
            text="🗑️ Delete",
            command=self.delete_selected_mod,
            bg=self.THEME_DANGER,
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            activebackground="#da190b"
        ).pack(side=tk.LEFT, padx=3)
        
        # Separator
        tk.Frame(btn_frame, bg="#404040", width=2, height=35).pack(side=tk.LEFT, padx=15)
        
        # Batch operations
        tk.Label(
            btn_frame,
            text="Batch:",
            font=("Segoe UI", 9, "bold"),
            bg=self.THEME_BG_PANEL,
            fg=self.THEME_TEXT_DIM
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="✓ All",
            command=self.enable_all_mods,
            bg="#2e7d32",
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=18,
            pady=8,
            cursor="hand2",
            activebackground="#256428"
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            btn_frame,
            text="✗ All",
            command=self.disable_all_mods,
            bg="#F57C00",
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=18,
            pady=8,
            cursor="hand2",
            activebackground="#db6f00"
        ).pack(side=tk.LEFT, padx=3)
        
        # Separator
        tk.Frame(btn_frame, bg="#404040", width=2, height=35).pack(side=tk.LEFT, padx=15)
        
        # Profiles button
        tk.Button(
            btn_frame,
            text="📋 Profiles",
            command=self.open_profiles,
            bg=self.THEME_PURPLE,
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            activebackground="#7B1FA2"
        ).pack(side=tk.LEFT, padx=3)
        
        # Separator
        tk.Frame(btn_frame, bg="#404040", width=2, height=35).pack(side=tk.LEFT, padx=15)
        
        # Restart Game button
        tk.Button(
            btn_frame,
            text="🔄 Restart Game",
            command=self.restart_game_with_changes,
            bg=self.THEME_ACCENT,
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            activebackground=self.THEME_ACCENT_HOVER
        ).pack(side=tk.LEFT, padx=3)
    
    def on_drop(self, event):
        """Handle file drop event"""
        files = self.root.tk.splitlist(event.data)
        for file_path in files:
            file_path = file_path.strip('{}')  # Remove curly braces if present
            if file_path.lower().endswith(('.zip', '.rar')):
                self.install_mod(file_path)
            else:
                messagebox.showwarning("Invalid File", f"File must be .zip or .rar\n{file_path}")
    
    def browse_archive(self):
        """Open file browser to select archive"""
        file_path = filedialog.askopenfilename(
            title="Select Mod Archive",
            filetypes=[("Archive Files", "*.zip *.rar"), ("All Files", "*.*")]
        )
        if file_path:
            self.install_mod(file_path)
    
    def install_mod(self, archive_path):
        """Extract and install a mod from an archive"""
        if not self.config['Paths']['brickadia_paks']:
            messagebox.showerror("Error", "Please configure Brickadia Paks folder in Settings first!")
            self.open_settings()
            return
        
        try:
            # Get archive name without extension
            archive_name = Path(archive_path).stem
            
            # Create temporary extraction folder
            temp_extract = Path(self.mods_storage_path) / f"temp_{archive_name}"
            os.makedirs(temp_extract, exist_ok=True)
            
            # Extract archive
            if archive_path.lower().endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_extract)
            elif archive_path.lower().endswith('.rar'):
                try:
                    with rarfile.RarFile(archive_path, 'r') as rar_ref:
                        rar_ref.extractall(temp_extract)
                except rarfile.RarCannotExec as e:
                    shutil.rmtree(temp_extract, ignore_errors=True)
                    
                    # Check if WinRAR is actually installed
                    winrar_paths = [
                        r"C:\Program Files\WinRAR\UnRAR.exe",
                        r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
                    ]
                    installed = any(os.path.exists(p) for p in winrar_paths)
                    
                    if installed:
                        error_msg = (
                            "Cannot extract .rar file - WinRAR is installed but not accessible.\n\n"
                            "This might be a permissions issue.\n\n"
                            "Solutions:\n"
                            "1. Try converting your mod to a .zip file instead\n"
                            "2. Run the mod loader as administrator\n"
                            "3. Reinstall WinRAR\n\n"
                            f"Error details: {str(e)}"
                        )
                    else:
                        error_msg = (
                            "Cannot extract .rar files - WinRAR/UnRAR not found.\n\n"
                            "Solutions:\n"
                            "1. Install WinRAR from: https://www.win-rar.com/download.html\n"
                            "2. Or convert your mod to a .zip file instead\n\n"
                            ".zip files work without any additional software!"
                        )
                    
                    messagebox.showerror("RAR Extraction Failed", error_msg)
                    return
                except Exception as e:
                    shutil.rmtree(temp_extract, ignore_errors=True)
                    messagebox.showerror(
                        "RAR Extraction Failed",
                        f"Error extracting RAR file:\n{str(e)}\n\n"
                        "Try converting your mod to a .zip file instead."
                    )
                    return
            
            # Detect mod type: PAK or UE4SS
            pak_files = list(temp_extract.rglob("*.pak"))
            
            # UE4SS mod files: Lua scripts, Blueprint assets, C++ binaries
            lua_files = list(temp_extract.rglob("*.lua"))
            blueprint_files = list(temp_extract.rglob("*.uasset")) + list(temp_extract.rglob("*.umap"))
            cpp_files = list(temp_extract.rglob("*.dll"))  # Compiled C++ mods
            
            # Determine mod type
            ue4ss_files = lua_files + blueprint_files + cpp_files
            is_ue4ss_mod = False
            
            if ue4ss_files and not pak_files:
                is_ue4ss_mod = True
            elif not pak_files and not ue4ss_files:
                messagebox.showerror("Error", "No valid mod files found in the archive!\n\nSupported formats:\n- PAK mods: .pak files\n- UE4SS mods: .lua, .uasset, .umap, .dll files")
                shutil.rmtree(temp_extract)
                return
            
            # Handle UE4SS mods differently
            if is_ue4ss_mod:
                self.install_ue4ss_mod(temp_extract, archive_name)
                return
            
            # Find all additional files (ucas, utoc, sig, etc.) that might come with the pak
            all_mod_files = []
            for pak_file in pak_files:
                # Add the pak file
                all_mod_files.append(pak_file)
                
                # Look for related files with same base name
                base_name = pak_file.stem
                parent_dir = pak_file.parent
                
                for ext in ['.ucas', '.utoc', '.sig', '.ini', '.txt']:
                    related_file = parent_dir / f"{base_name}{ext}"
                    if related_file.exists() and related_file not in all_mod_files:
                        all_mod_files.append(related_file)
            
            # Look for modinfo.json
            mod_info = None
            modinfo_files = list(temp_extract.rglob("modinfo.json"))
            if modinfo_files:
                try:
                    with open(modinfo_files[0], 'r', encoding='utf-8') as f:
                        mod_info = json.load(f)
                except:
                    mod_info = None
            
            # Look for icon
            icon_path = None
            if mod_info and 'icon' in mod_info:
                icon_files = list(temp_extract.rglob(mod_info['icon']))
                if icon_files:
                    icon_path = icon_files[0]
            
            # Move pak files and related files to mods storage
            for pak_file in pak_files:
                mod_name = pak_file.stem
                
                # Use custom name from modinfo if available
                if mod_info and 'name' in mod_info:
                    display_name = mod_info['name']
                else:
                    display_name = mod_name
                
                # Create a folder for this mod
                mod_folder = Path(self.mods_storage_path) / mod_name
                counter = 1
                while mod_folder.exists():
                    mod_folder = Path(self.mods_storage_path) / f"{mod_name}_{counter}"
                    counter += 1
                
                os.makedirs(mod_folder, exist_ok=True)
                
                # Copy all related files for this mod
                related_files = [f for f in all_mod_files if f.stem == mod_name]
                file_list = []
                
                for file in related_files:
                    dest_file = mod_folder / file.name
                    shutil.copy2(file, dest_file)
                    file_list.append(file.name)
                
                # Copy icon if available
                icon_dest = None
                if icon_path:
                    icon_dest = mod_folder / f"icon{icon_path.suffix}"
                    shutil.copy2(icon_path, icon_dest)
                
                # Add to mods database
                mod_id = mod_folder.name
                self.mods[mod_id] = {
                    'name': display_name,
                    'folder': str(mod_folder),
                    'files': file_list,
                    'enabled': False,
                    'description': mod_info.get('description', '') if mod_info else '',
                    'author': mod_info.get('author', '') if mod_info else '',
                    'version': mod_info.get('version', '') if mod_info else '',
                    'icon': str(icon_dest) if icon_dest else ''
                }
            
            # Clean up temp folder
            shutil.rmtree(temp_extract)
            
            # Save mods database
            self.save_mods()
            self.refresh_mod_list()
            
            messagebox.showinfo("Success", f"Installed {len(pak_files)} mod(s) from {archive_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install mod:\n{str(e)}")
    
    def configure_ue4ss_settings(self, ue4ss_path):
        """Configure UE4SS settings.ini file with recommended settings"""
        try:
            settings_file = ue4ss_path / 'UE4SS-settings.ini'
            
            settings_content = """[Overrides]
; Path to the 'Mods' folder
; Default: <dll_directory>/Mods
ModsFolderPath =

[General]
EnableHotReloadSystem = 1

; Whether the cache system for AOBs will be used.
; Default: 1
UseCache = 1

; Whether caches will be invalidated if ue4ss.dll has changed
; Default: 1
InvalidateCacheIfDLLDiffers = 1

; The number of seconds the scanner will scan for before giving up
; Default: 30
SecondsToScanBeforeGivingUp = 25

; Whether to create UObject listeners in GUObjectArray to create a fast cache for use instead of iterating GUObjectArray.
; Setting this to false can help if you're experiencing a crash on startup.
; Default: true
bUseUObjectArrayCache = true

[EngineVersionOverride]
MajorVersion = 5
MinorVersion = 5
; True if the game is built as Debug, Development, or Test.
; Default: false
DebugBuild = 

[ObjectDumper]
; Whether to force all assets to be loaded before dumping objects
; WARNING: Can require multiple gigabytes of extra memory
; WARNING: Is not stable & will crash the game if you load past the main menu after dumping
; Default: 0
LoadAllAssetsBeforeDumpingObjects = 0

; Whether to display the offset from the main executable for functions instead of the function pointer
; Default: 0
UseModuleOffsets = 0

[CXXHeaderGenerator]
; Whether to property offsets and sizes
; Default: 1
DumpOffsetsAndSizes = 1

; Whether memory layouts of classes and structs should be accurate
; This must be set to 1, if you want to use the generated headers in an actual C++ project
; When set to 0, padding member variables will not be generated
; NOTE: A VALUE OF 1 HAS NO PURPOSE YET! MEMORY LAYOUT IS NOT ACCURATE EITHER WAY!
; Default: 0
KeepMemoryLayout = 0

; Whether to force all assets to be loaded before generating headers
; WARNING: Can require multiple gigabytes of extra memory
; WARNING: Is not stable & will crash the game if you load past the main menu after dumping
; Default: 0
LoadAllAssetsBeforeGeneratingCXXHeaders = 0

[UHTHeaderGenerator]
; Whether to skip generating packages that belong to the engine
; Some games make alterations to the engine and for those games you might want to set this to 0
; Default: 0
IgnoreAllCoreEngineModules = 0

; Whether to skip generating the "Engine" and "CoreUObject" packages
; Default: 0
IgnoreEngineAndCoreUObject = 0

; Whether to force all UFUNCTION macros to have "BlueprintCallable"
; Note: This will cause some errors in the generated headers that you will need to manually fix
; Default: 1
MakeAllFunctionsBlueprintCallable = 1

; Whether to force all UPROPERTY macros to have "BlueprintReadWrite"
; Also forces all UPROPERTY macros to have "meta=(AllowPrivateAccess=true)"
; Default: 1
MakeAllPropertyBlueprintsReadWrite = 1

; Whether to force UENUM macros on enums to have 'BlueprintType' if the underlying type was implicit or uint8
; Note: This also forces the underlying type to be uint8 where the type would otherwise be implicit
; Default: 1
MakeEnumClassesBlueprintType = 1

; Whether to force "Config = Engine" on all UCLASS macros that use either one of:
; "DefaultConfig", "GlobalUserConfig" or "ProjectUserConfig"
; Default: 1
MakeAllConfigsEngineConfig = 1

[Debug]
; Whether to enable the external UE4SS debug console.
ConsoleEnabled = 1
GuiConsoleEnabled = 1
GuiConsoleVisible = 1

; Multiplier for Font Size within the Debug Gui
; Default: 1
GuiConsoleFontScaling = 1

; The API that will be used to render the GUI debug window.
; Valid values (case-insensitive): dx11, d3d11, opengl
; Default: opengl
GraphicsAPI = d3d11

; The method with which the GUI will be rendered.
; Valid values (case-insensitive):
; ExternalThread: A separate thread will be used.
; EngineTick: The UEngine::Tick function will be used.
; GameViewportClientTick: The UGameViewportClient::Tick function will be used.
; Default: ExternalThread
RenderMode = ExternalThread

[Threads]
; The number of threads that the sig scanner will use (not real cpu threads, can be over your physical & hyperthreading max)
; If the game is modular then multi-threading will always be off regardless of the settings in this file
; Min: 1
; Max: 4294967295
; Default: 8
SigScannerNumThreads = 4

; The minimum size that a module has to be in order for multi-threading to be enabled
; This should be large enough so that the cost of creating threads won't out-weigh the speed gained from scanning in multiple threads
; Min: 0
; Max: 4294967295
; Default: 16777216
SigScannerMultithreadingModuleSizeThreshold = 16777216

[Memory]
; The maximum memory usage (in percentage, see Task Manager %) allowed before asset loading (when LoadAllAssetsBefore* is 1) cannot happen.
; Once this percentage is reached, the asset loader will stop loading and whatever operation was in progress (object dump, or cxx generator) will continue.
; Default: 85
MaxMemoryUsageDuringAssetLoading = 85

[Hooks]
HookProcessInternal = 1
HookProcessLocalScriptFunction = 1
HookInitGameState = 1
HookLoadMap = 1
HookCallFunctionByNameWithArguments = 1
HookBeginPlay = 1
HookLocalPlayerExec = 1
HookAActorTick = 1
HookEngineTick = 1
HookGameViewportClientTick = 1
FExecVTableOffsetInLocalPlayer = 0x28

[CrashDump]
EnableDumping = 1
FullMemoryDump = 0

[ExperimentalFeatures]
"""
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                f.write(settings_content)
                
        except Exception as e:
            print(f"Warning: Failed to configure UE4SS settings: {e}")
    
    def uninstall_ue4ss(self):
        """Uninstall UE4SS from Brickadia"""
        try:
            if not self.config['Paths']['brickadia_paks']:
                messagebox.showerror("Error", "Please configure Brickadia Paks folder in Settings first!")
                return
            
            game_base = Path(self.config['Paths']['brickadia_paks']).parent.parent
            ue4ss_path = game_base / 'Binaries' / 'Win64'
            ue4ss_dll = ue4ss_path / 'UE4SS.dll'
            
            if not ue4ss_dll.exists():
                messagebox.showinfo("Not Installed", "UE4SS is not currently installed.")
                return
            
            result = messagebox.askyesno(
                "Confirm Uninstall",
                "Are you sure you want to uninstall UE4SS?\n\n"
                "This will remove:\n"
                "- UE4SS.dll\n"
                "- UE4SS-settings.ini\n"
                "- dwmapi.dll (UE4SS proxy)\n"
                "- Related UE4SS files\n\n"
                "Your installed mods will remain but won't work until UE4SS is reinstalled.\n\n"
                "Continue with uninstallation?"
            )
            
            if not result:
                return
            
            # First, disable all UE4SS mods
            ue4ss_mods_disabled = 0
            for mod_id, mod in self.mods.items():
                if mod.get('mod_type') == 'UE4SS' and mod.get('enabled'):
                    self.disable_mod(mod_id)
                    ue4ss_mods_disabled += 1
            
            # List of UE4SS files to remove
            ue4ss_files = [
                'UE4SS.dll',
                'UE4SS.pdb',
                'UE4SS-settings.ini',
                'dwmapi.dll',
                'dwmapi.pdb',
                'UE4SS_Signatures'
            ]
            
            removed_count = 0
            for file_name in ue4ss_files:
                file_path = ue4ss_path / file_name
                if file_path.exists():
                    if file_path.is_file():
                        file_path.unlink()
                        removed_count += 1
                    elif file_path.is_dir():
                        shutil.rmtree(file_path, ignore_errors=True)
                        removed_count += 1
            
            # Refresh the mod list to show disabled mods
            self.refresh_mod_list()
            
            messagebox.showinfo(
                "Uninstalled",
                f"UE4SS has been successfully uninstalled!\n\n"
                f"Removed {removed_count} UE4SS file(s)/folder(s).\n"
                f"Disabled {ue4ss_mods_disabled} UE4SS mod(s).\n\n"
                "Your UE4SS mods remain installed but are now disabled.\n"
                "They will be re-enabled when you reinstall UE4SS."
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to uninstall UE4SS:\n{str(e)}")
    
    def download_and_install_ue4ss(self):
        """Download and install UE4SS for Brickadia using br_patcher.exe"""
        try:
            game_base = Path(self.config['Paths']['brickadia_paks']).parent.parent
            ue4ss_path = game_base / 'Binaries' / 'Win64'
            
            # Download URLs from br-lua-patcher release
            br_patcher_url = "https://github.com/brickadia-community/br-lua-patcher/releases/download/latest/br_patcher.exe"
            dwmapi_url = "https://github.com/brickadia-community/br-lua-patcher/releases/download/latest/dwmapi.dll"
            ue4ss_dll_url = "https://github.com/brickadia-community/br-lua-patcher/releases/download/latest/UE4SS.dll"
            
            # Show progress dialog
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Installing UE4SS")
            progress_window.geometry("400x150")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            # Center the window
            progress_window.update_idletasks()
            x = (progress_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
            progress_window.geometry(f"400x150+{x}+{y}")
            
            status_label = tk.Label(progress_window, text="Downloading files...", font=("Segoe UI", 10))
            status_label.pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_window, length=350, mode='indeterminate')
            progress_bar.pack(pady=10)
            progress_bar.start(10)
            
            progress_window.update()
            
            # Step 1: Download all required files to Brickadia binary directory
            os.makedirs(ue4ss_path, exist_ok=True)
            
            status_label.config(text="Downloading br_patcher.exe...")
            progress_window.update()
            br_patcher_path = ue4ss_path / "br_patcher.exe"
            urllib.request.urlretrieve(br_patcher_url, br_patcher_path)
            
            status_label.config(text="Downloading UE4SS DLLs...")
            progress_window.update()
            
            dwmapi_path = ue4ss_path / "dwmapi.dll"
            urllib.request.urlretrieve(dwmapi_url, dwmapi_path)
            
            ue4ss_dll_path = ue4ss_path / "UE4SS.dll"
            urllib.request.urlretrieve(ue4ss_dll_url, ue4ss_dll_path)
            
            # Step 2: Run br_patcher.exe from the Brickadia directory
            progress_bar.stop()
            progress_window.destroy()
            
            # Show instructions to user
            result = messagebox.askokcancel(
                "Run Patcher",
                f"The br_patcher.exe has been downloaded to:\n{ue4ss_path}\n\n"
                "A console window will now open.\n"
                "Please follow the prompts in the window to patch Brickadia.\n\n"
                "Click OK to continue, then press any key in the console window when prompted."
            )
            
            if not result:
                raise Exception("User cancelled patching process")
            
            import subprocess
            # Run the patcher with a visible console window
            process = subprocess.Popen(
                [str(br_patcher_path)],
                cwd=str(ue4ss_path),
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Wait for the user to complete the patching
            process.wait()
            
            # Show progress dialog again
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Installing UE4SS")
            progress_window.geometry("400x150")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_window.update_idletasks()
            x = (progress_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
            progress_window.geometry(f"400x150+{x}+{y}")
            
            status_label = tk.Label(progress_window, text="Finalizing installation...", font=("Segoe UI", 10))
            status_label.pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_window, length=350, mode='indeterminate')
            progress_bar.pack(pady=10)
            progress_bar.start(10)
            progress_window.update()
            
            # Step 3: Create Mods folder
            status_label.config(text="Setting up Mods folder...")
            progress_window.update()
            
            mods_folder = ue4ss_path / "Mods"
            os.makedirs(mods_folder, exist_ok=True)
            
            # Step 4: Configure settings.ini
            status_label.config(text="Configuring UE4SS settings...")
            progress_window.update()
            
            self.configure_ue4ss_settings(ue4ss_path)
            
            progress_bar.stop()
            progress_window.destroy()
            
            messagebox.showinfo(
                "Success",
                "UE4SS has been successfully installed for Brickadia!\n\n"
                "✓ Brickadia executable has been patched (br_patcher.exe)\n"
                "✓ UE4SS DLLs installed (br-lua-patcher build)\n"
                "✓ Settings configured for optimal performance\n"
                f"✓ Mods folder created: {mods_folder}\n\n"
                "You can now enable your Lua/Blueprint/C++ mods!"
            )
            return True
            
        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            error_msg = str(e)
            messagebox.showerror(
                "Installation Failed",
                f"Failed to install UE4SS:\n{error_msg}\n\n"
                "The br_patcher.exe has been downloaded to:\n"
                f"{ue4ss_path}\n\n"
                "Please try running it manually from that location."
            )
            return False
    
    def install_ue4ss_mod(self, temp_extract, archive_name):
        """Install a UE4SS mod (Lua, Blueprint, or C++)"""
        try:
            # Find all UE4SS mod files
            lua_files = list(temp_extract.rglob("*.lua"))
            blueprint_files = list(temp_extract.rglob("*.uasset")) + list(temp_extract.rglob("*.umap"))
            cpp_files = list(temp_extract.rglob("*.dll"))
            all_files = list(temp_extract.rglob("*"))
            all_files = [f for f in all_files if f.is_file()]
            
            # Detect mod subtype
            mod_subtype = []
            if lua_files:
                mod_subtype.append("Lua")
            if blueprint_files:
                mod_subtype.append("Blueprint")
            if cpp_files:
                mod_subtype.append("C++")
            
            mod_subtype_str = "/".join(mod_subtype) if mod_subtype else "UE4SS"
            
            # Look for modinfo.json
            mod_info = None
            modinfo_files = list(temp_extract.rglob("modinfo.json"))
            if modinfo_files:
                try:
                    with open(modinfo_files[0], 'r', encoding='utf-8') as f:
                        mod_info = json.load(f)
                except:
                    mod_info = None
            
            # Determine mod name
            if mod_info and 'name' in mod_info:
                display_name = mod_info['name']
                mod_name = display_name.replace(' ', '_')
            else:
                display_name = archive_name
                mod_name = archive_name
            
            # Create mod folder
            mod_folder = Path(self.mods_storage_path) / mod_name
            counter = 1
            while mod_folder.exists():
                mod_folder = Path(self.mods_storage_path) / f"{mod_name}_{counter}"
                counter += 1
            
            os.makedirs(mod_folder, exist_ok=True)
            
            # Copy all files
            file_list = []
            for file in all_files:
                relative_path = file.relative_to(temp_extract)
                dest_file = mod_folder / relative_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest_file)
                file_list.append(str(relative_path))
            
            # Look for icon
            icon_dest = None
            if mod_info and 'icon' in mod_info:
                icon_files = list(temp_extract.rglob(mod_info['icon']))
                if icon_files:
                    icon_dest = mod_folder / f"icon{icon_files[0].suffix}"
                    shutil.copy2(icon_files[0], icon_dest)
            
            # Add to mods database
            mod_id = mod_folder.name
            default_desc = f"UE4SS Mod ({mod_subtype_str})"
            self.mods[mod_id] = {
                'name': display_name,
                'folder': str(mod_folder),
                'files': file_list,
                'enabled': False,
                'mod_type': 'UE4SS',  # Mark as UE4SS mod
                'description': mod_info.get('description', default_desc) if mod_info else default_desc,
                'author': mod_info.get('author', '') if mod_info else '',
                'version': mod_info.get('version', '') if mod_info else '',
                'icon': str(icon_dest) if icon_dest else ''
            }
            
            # Clean up
            shutil.rmtree(temp_extract)
            
            # Save and refresh
            self.save_mods()
            self.refresh_mod_list()
            
            # Check if UE4SS is installed
            game_base = Path(self.config['Paths']['brickadia_paks']).parent.parent
            ue4ss_dll = game_base / 'Binaries' / 'Win64' / 'UE4SS.dll'
            
            if ue4ss_dll.exists():
                messagebox.showinfo("Success", f"Installed UE4SS mod: {display_name}\nType: {mod_subtype_str}\n\n✓ UE4SS detected in your Brickadia folder.")
            else:
                # Offer to download UE4SS
                result = messagebox.askyesnocancel(
                    "UE4SS Not Found",
                    f"Installed UE4SS mod: {display_name}\nType: {mod_subtype_str}\n\n"
                    "⚠ WARNING: UE4SS is not installed!\n\n"
                    "This mod requires UE4SS to work.\n\n"
                    "Would you like to download and install UE4SS automatically?\n\n"
                    "Yes = Download and install UE4SS now\n"
                    "No = I'll install it manually later\n"
                    "Cancel = View installation instructions"
                )
                
                if result is True:  # Yes - download
                    self.download_and_install_ue4ss()
                elif result is None:  # Cancel - show instructions
                    messagebox.showinfo(
                        "Manual Installation Instructions",
                        "To install UE4SS for Brickadia manually:\n\n"
                        "1. Download br_patcher.exe from:\n"
                        "   https://github.com/brickadia-community/br-lua-patcher/releases\n"
                        "2. Run br_patcher.exe in your Brickadia folder\n"
                        "3. Follow prompts to patch the game\n\n"
                        "This will install UE4SS specifically compiled for Brickadia.\n\n"
                        "The mod has been installed but will not work until UE4SS is installed."
                    )
            
        except Exception as e:
            shutil.rmtree(temp_extract, ignore_errors=True)
            messagebox.showerror("Error", f"Failed to install UE4SS mod:\n{str(e)}")
    
    def enable_selected_mod(self):
        """Enable the selected mod"""
        selection = self.mod_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mod to enable")
            return
        
        for item in selection:
            mod_id = item  # The item ID is the mod_id
            
            if mod_id in self.mods:
                self.enable_mod(mod_id)
        
        self.refresh_mod_list()
    
    def disable_selected_mod(self):
        """Disable the selected mod"""
        selection = self.mod_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mod to disable")
            return
        
        for item in selection:
            mod_id = item  # The item ID is the mod_id
            
            if mod_id in self.mods:
                self.disable_mod(mod_id)
        
        self.refresh_mod_list()
    
    def delete_selected_mod(self):
        """Delete the selected mod"""
        selection = self.mod_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mod to delete")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected mod(s)?")
        if not confirm:
            return
        
        for item in selection:
            mod_id = item  # The item ID is the mod_id
            
            if mod_id in self.mods:
                self.delete_mod(mod_id)
        
        self.refresh_mod_list()
    
    def enable_mod(self, mod_id):
        """Enable a mod by copying all its files to appropriate folder"""
        mod = self.mods[mod_id]
        
        if mod['enabled']:
            messagebox.showinfo("Info", f"{mod['name']} is already enabled")
            return
        
        try:
            mod_folder = Path(mod['folder'])
            mod_type = mod.get('mod_type', 'PAK')  # Default to PAK for old mods
            
            if not mod_folder.exists():
                messagebox.showerror("Error", f"Mod folder not found:\n{mod_folder}")
                return
            
            if mod_type == 'UE4SS':
                # UE4SS mods go to Brickadia/Binaries/Win64/Mods/
                game_base = Path(self.config['Paths']['brickadia_paks']).parent.parent
                ue4ss_mods = game_base / 'Binaries' / 'Win64' / 'Mods' / mod['name'].replace(' ', '_')
                
                # Check if UE4SS is installed
                ue4ss_dll = game_base / 'Binaries' / 'Win64' / 'UE4SS.dll'
                if not ue4ss_dll.exists():
                    result = messagebox.askyesnocancel(
                        "UE4SS Not Found",
                        "⚠ UE4SS is NOT installed in your Brickadia folder!\n\n"
                        "This UE4SS mod requires UE4SS to work.\n\n"
                        "Would you like to download and install UE4SS now?\n\n"
                        "Yes = Download and install UE4SS, then enable mod\n"
                        "No = Enable mod anyway (won't work until UE4SS is installed)\n"
                        "Cancel = Don't enable the mod"
                    )
                    
                    if result is True:  # Yes - download UE4SS
                        if self.download_and_install_ue4ss():
                            # Continue enabling the mod after successful installation
                            pass
                        else:
                            return  # Download failed, abort
                    elif result is False:  # No - enable anyway
                        pass  # Continue with enabling
                    else:  # Cancel
                        return
                
                os.makedirs(ue4ss_mods, exist_ok=True)
                
                # Copy all mod files preserving structure
                game_paths = []
                for file_name in mod['files']:
                    source = mod_folder / file_name
                    destination = ue4ss_mods / file_name
                    
                    if source.exists():
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, destination)
                        game_paths.append(str(destination))
                
                mod['enabled'] = True
                mod['game_paths'] = game_paths
                self.save_mods()
                
                messagebox.showinfo("Success", f"Enabled UE4SS mod: {mod['name']}")
            else:
                # Regular PAK mods go to Paks folder
                game_paks = Path(self.config['Paths']['brickadia_paks'])
                
                # Copy all mod files to game directory
                game_paths = []
                for file_name in mod['files']:
                    source = mod_folder / file_name
                    destination = game_paks / file_name
                    
                    if source.exists():
                        shutil.copy2(source, destination)
                        game_paths.append(str(destination))
                
                mod['enabled'] = True
                mod['game_paths'] = game_paths
                self.save_mods()
                
                messagebox.showinfo("Success", f"Enabled: {mod['name']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enable mod:\n{str(e)}")
    
    def disable_mod(self, mod_id):
        """Disable a mod by removing all its files from Brickadia paks folder"""
        mod = self.mods[mod_id]
        
        if not mod['enabled']:
            messagebox.showinfo("Info", f"{mod['name']} is already disabled")
            return
        
        try:
            mod_type = mod.get('mod_type', 'PAK')
            
            if mod_type == 'UE4SS':
                # For UE4SS mods, remove the entire mod folder
                game_base = Path(self.config['Paths']['brickadia_paks']).parent.parent
                ue4ss_mod_folder = game_base / 'Binaries' / 'Win64' / 'Mods' / mod['name'].replace(' ', '_')
                
                if ue4ss_mod_folder.exists():
                    shutil.rmtree(ue4ss_mod_folder)
            else:
                # For PAK mods, remove individual files
                for game_path_str in mod.get('game_paths', []):
                    game_path = Path(game_path_str)
                    if game_path.exists():
                        os.remove(game_path)
            
            mod['enabled'] = False
            if 'game_paths' in mod:
                del mod['game_paths']
            self.save_mods()
            
            messagebox.showinfo("Success", f"Disabled: {mod['name']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disable mod:\n{str(e)}")
    
    def delete_mod(self, mod_id):
        """Delete a mod completely"""
        mod = self.mods[mod_id]
        
        try:
            # Disable first if enabled
            if mod['enabled']:
                self.disable_mod(mod_id)
            
            # Delete mod folder and all its contents
            mod_folder = Path(mod['folder'])
            if mod_folder.exists():
                shutil.rmtree(mod_folder)
            
            # Remove from database
            del self.mods[mod_id]
            self.save_mods()
            
            messagebox.showinfo("Success", f"Deleted: {mod['name']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete mod:\n{str(e)}")
    
    def refresh_mod_list(self):
        """Refresh the mod list display - uses filter_mods to apply current filters"""
        self.filter_mods()
        self.update_load_order_list()
        # Check for duplicates automatically
        self.check_for_duplicates_silent()
    
    def check_for_duplicates_silent(self):
        """Silently check for duplicates and update UI indicator"""
        duplicates = self.find_duplicate_mods()
        # You could add a visual indicator here if duplicates are found
        if duplicates:
            print(f"Warning: {len(duplicates)} duplicate mod(s) detected")
    
    def find_duplicate_mods(self):
        """Find duplicate mods by name or file"""
        duplicates = []
        seen_names = {}
        seen_files = {}
        
        for mod_id, mod in self.mods.items():
            mod_name = mod['name'].lower()
            
            # Check for duplicate names
            if mod_name in seen_names:
                duplicates.append({
                    'type': 'name',
                    'mod1': seen_names[mod_name],
                    'mod2': mod_id,
                    'name': mod['name']
                })
            else:
                seen_names[mod_name] = mod_id
            
            # Check for duplicate PAK files
            for file_name in mod['files']:
                file_lower = file_name.lower()
                if file_lower in seen_files:
                    duplicates.append({
                        'type': 'file',
                        'mod1': seen_files[file_lower],
                        'mod2': mod_id,
                        'file': file_name
                    })
                else:
                    seen_files[file_lower] = mod_id
        
        return duplicates
    
    def check_for_duplicates(self):
        """Show dialog with duplicate mods information"""
        duplicates = self.find_duplicate_mods()
        
        if not duplicates:
            messagebox.showinfo(
                "No Duplicates Found",
                "✓ No duplicate mods detected!\n\n"
                "All your mods have unique names and files."
            )
            return
        
        # Create detailed message
        dup_by_name = [d for d in duplicates if d['type'] == 'name']
        dup_by_file = [d for d in duplicates if d['type'] == 'file']
        
        message = f"⚠️ Found {len(duplicates)} potential duplicate(s):\n\n"
        
        if dup_by_name:
            message += f"📝 Duplicate Names ({len(dup_by_name)}):\n"
            for dup in dup_by_name[:5]:  # Show first 5
                mod1_name = self.mods[dup['mod1']]['name']
                mod2_name = self.mods[dup['mod2']]['name']
                message += f"  • {dup['name']}\n"
            if len(dup_by_name) > 5:
                message += f"  ... and {len(dup_by_name) - 5} more\n"
            message += "\n"
        
        if dup_by_file:
            message += f"📦 Duplicate Files ({len(dup_by_file)}):\n"
            for dup in dup_by_file[:5]:  # Show first 5
                message += f"  • {dup['file']}\n"
            if len(dup_by_file) > 5:
                message += f"  ... and {len(dup_by_file) - 5} more\n"
            message += "\n"
        
        message += "Having duplicate mods may cause conflicts!\nConsider removing or disabling duplicates."
        
        messagebox.showwarning("Duplicate Mods Detected", message)
    
    def update_load_order_list(self):
        """Update the load order display with enabled mods and their icons"""
        # Clear existing items
        for item in self.order_items:
            item.destroy()
        self.order_items.clear()
        
        # Get all enabled mods sorted by load order
        enabled_mods = [(mod_id, mod) for mod_id, mod in self.mods.items() if mod['enabled']]
        enabled_mods.sort(key=lambda x: x[1].get('load_order', 999))
        
        for i, (mod_id, mod) in enumerate(enabled_mods, 1):
            self.create_load_order_item(i, mod_id, mod)
        
        # Update canvas scroll region
        self.order_canvas.update_idletasks()
        self.order_canvas.configure(scrollregion=self.order_canvas.bbox("all"))
    
    def create_load_order_item(self, index, mod_id, mod):
        """Create a visual load order item with icon and info"""
        # Create item frame
        item_frame = tk.Frame(
            self.order_inner_frame,
            bg="#353535",
            bd=0,
            highlightthickness=1,
            highlightbackground="#404040"
        )
        item_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Store mod_id as attribute
        item_frame.mod_id = mod_id
        item_frame.index = index
        self.order_items.append(item_frame)
        
        # Left side: Number badge
        number_frame = tk.Frame(item_frame, bg="#2d2d2d", width=35)
        number_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        number_frame.pack_propagate(False)
        
        number_label = tk.Label(
            number_frame,
            text=f"#{index}",
            font=("Segoe UI", 9, "bold"),
            bg="#2d2d2d",
            fg=self.THEME_ACCENT
        )
        number_label.pack(expand=True)
        
        # Mod icon
        icon_label = tk.Label(item_frame, bg="#353535")
        icon_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Load icon or use fallback
        icon_image = self.get_load_order_icon(mod_id, mod)
        icon_label.config(image=icon_image)
        icon_label.image = icon_image  # Keep reference
        
        # Right side: Mod info
        info_frame = tk.Frame(item_frame, bg="#353535")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Mod name
        name_label = tk.Label(
            info_frame,
            text=mod['name'],
            font=("Segoe UI", 10, "bold"),
            bg="#353535",
            fg=self.THEME_TEXT,
            anchor="w"
        )
        name_label.pack(fill=tk.X)
        
        # Mod metadata (version and author)
        metadata_parts = []
        if mod.get('version'):
            metadata_parts.append(f"v{mod['version']}")
        if mod.get('author'):
            author_display = mod['author'][:20] + "..." if len(mod['author']) > 20 else mod['author']
            metadata_parts.append(f"by {author_display}")
        
        if metadata_parts:
            metadata_label = tk.Label(
                info_frame,
                text=" • ".join(metadata_parts),
                font=("Segoe UI", 8),
                bg="#353535",
                fg=self.THEME_TEXT_DIM,
                anchor="w"
            )
            metadata_label.pack(fill=tk.X)
        
        # Bind drag events to all components
        for widget in [item_frame, number_frame, number_label, icon_label, info_frame, name_label]:
            widget.bind('<Button-1>', self.on_load_order_click)
            widget.bind('<B1-Motion>', self.on_load_order_drag)
            widget.bind('<ButtonRelease-1>', self.on_load_order_drop)
            widget.bind('<Enter>', lambda e, f=item_frame: f.config(bg="#404040"))
            widget.bind('<Leave>', lambda e, f=item_frame: f.config(bg="#353535"))
    
    def get_load_order_icon(self, mod_id, mod):
        """Get or create icon for load order display"""
        # Check cache first
        if mod_id in self.load_order_icons:
            return self.load_order_icons[mod_id]
        
        # Try to load mod's icon
        icon_path = mod.get('icon', '')
        if icon_path and Path(icon_path).exists():
            try:
                from PIL import Image, ImageTk
                img = Image.open(icon_path)
                img = img.resize((40, 40), Image.Resampling.LANCZOS)
                icon_image = ImageTk.PhotoImage(img)
                self.load_order_icons[mod_id] = icon_image
                return icon_image
            except Exception as e:
                print(f"Failed to load icon for {mod['name']}: {e}")
        
        # Fallback to program logo without white background
        if self.logo_ui_photo:
            # Resize logo to 40x40 for load order
            try:
                from PIL import Image, ImageTk
                logo_resized = self.logo_ui.resize((40, 40), Image.Resampling.LANCZOS)
                icon_image = ImageTk.PhotoImage(logo_resized)
                self.load_order_icons[mod_id] = icon_image
                return icon_image
            except:
                pass
        
        # Ultimate fallback: create a simple colored square
        try:
            from PIL import Image, ImageTk
            fallback = Image.new('RGBA', (40, 40), (93, 173, 226, 255))  # Blue color
            icon_image = ImageTk.PhotoImage(fallback)
            self.load_order_icons[mod_id] = icon_image
            return icon_image
        except:
            return None
    
    def get_fallback_icon_for_tree(self, mod_id):
        """Get fallback icon for tree view (48x48)"""
        # Check if we already have a cached fallback for this mod
        cache_key = f"tree_{mod_id}"
        if cache_key in self.mod_icons:
            return self.mod_icons[cache_key]
        
        # Use program logo as fallback
        if self.logo_ui_photo:
            try:
                from PIL import Image, ImageTk
                logo_resized = self.logo_ui.resize((48, 48), Image.Resampling.LANCZOS)
                icon_image = ImageTk.PhotoImage(logo_resized)
                self.mod_icons[cache_key] = icon_image
                return icon_image
            except Exception as e:
                print(f"Failed to create fallback icon: {e}")
        
        # Ultimate fallback: create a simple colored square
        try:
            from PIL import Image, ImageTk
            fallback = Image.new('RGBA', (48, 48), (93, 173, 226, 255))  # Blue color
            icon_image = ImageTk.PhotoImage(fallback)
            self.mod_icons[cache_key] = icon_image
            return icon_image
        except:
            return None
    
    def move_mod_up(self):
        """Move selected mod up in load order"""
        # This function is deprecated with new visual load order
        # Drag and drop is now the primary method
        messagebox.showinfo("Tip", "Use drag-and-drop to reorder mods!\n\nClick and drag any mod in the load order list.")
    
    def move_mod_down(self):
        """Move selected mod down in load order"""
        # This function is deprecated with new visual load order
        # Drag and drop is now the primary method
        messagebox.showinfo("Tip", "Use drag-and-drop to reorder mods!\n\nClick and drag any mod in the load order list.")
    
    def on_load_order_click(self, event):
        """Handle mouse click on load order item"""
        # Find which item was clicked
        widget = event.widget
        # Traverse up to find the item frame
        while widget and widget != self.order_inner_frame:
            if hasattr(widget, 'mod_id'):
                self.drag_data["item"] = widget
                self.drag_data["start_y"] = event.y_root
                self.drag_data["index"] = self.order_items.index(widget)
                widget.config(cursor="hand2")
                return
            widget = widget.master
    
    def on_load_order_drag(self, event):
        """Handle dragging in load order list"""
        if self.drag_data["item"] is None:
            return
        
        # Only start dragging if mouse moved more than 5 pixels
        if abs(event.y_root - self.drag_data.get("start_y", 0)) < 5:
            return
        
        # Find where to insert based on mouse position
        current_index = self.drag_data["index"]
        item = self.drag_data["item"]
        
        # Calculate new position based on y coordinate
        for i, other_item in enumerate(self.order_items):
            if i == current_index:
                continue
            
            # Get the y position of this item
            y_pos = other_item.winfo_y()
            height = other_item.winfo_height()
            
            # Check if mouse is over this item
            if y_pos <= event.y_root - self.order_canvas.winfo_rooty() <= y_pos + height:
                if i != current_index:
                    # Move the item
                    self.order_items.pop(current_index)
                    self.order_items.insert(i, item)
                    self.drag_data["index"] = i
                    
                    # Re-pack items in new order
                    for item_widget in self.order_items:
                        item_widget.pack_forget()
                    for item_widget in self.order_items:
                        item_widget.pack(fill=tk.X, padx=5, pady=3)
                    
                    # Update numbers
                    self.renumber_load_order()
                    break
    
    def on_load_order_drop(self, event):
        """Handle mouse release after dragging"""
        if self.drag_data["item"]:
            self.drag_data["item"].config(cursor="")
        self.drag_data = {"index": None, "item": None, "start_y": None}
    
    def renumber_load_order(self):
        """Renumber the load order items after reordering"""
        for i, item in enumerate(self.order_items, 1):
            # Find the number label and update it
            for child in item.winfo_children():
                if isinstance(child, tk.Frame):
                    for label in child.winfo_children():
                        if isinstance(label, tk.Label) and label.cget('text').startswith('#'):
                            label.config(text=f"#{i}")
                            break
    
    def show_context_menu(self, event):
        """Show right-click context menu for mod"""
        print(f"Context menu triggered! Event: {event}, x={event.x}, y={event.y}")
        
        # Select the item under cursor
        item = self.mod_tree.identify_row(event.y)
        print(f"Identified item: {item}")
        if not item:
            print("No item found under cursor")
            return
            
        self.mod_tree.selection_set(item)
        
        # Get mod info - the item ID is the mod_id (key in self.mods)
        try:
            mod_id = item
            mod_data = self.mods.get(mod_id)
            
            if not mod_data:
                print(f"Mod data not found for ID: {mod_id}")
                return
            
            mod_name = mod_data['name']
            print(f"Creating context menu for: {mod_name}")
        except Exception as e:
            print(f"Error getting mod info: {e}")
            return
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0, 
                              bg="#2d2d2d", fg="#ffffff",
                              activebackground=self.THEME_ACCENT,
                              activeforeground="#ffffff")
        
        # Add menu items based on mod status
        if mod_data['enabled']:
            context_menu.add_command(label="✗ Disable Mod", 
                                    command=self.disable_selected_mod)
        else:
            context_menu.add_command(label="✓ Enable Mod", 
                                    command=self.enable_selected_mod)
        
        context_menu.add_separator()
        context_menu.add_command(label="🗑️ Delete Mod", 
                                command=self.delete_selected_mod)
        context_menu.add_separator()
        context_menu.add_command(label="📁 Open Mod Folder", 
                                command=lambda: self.open_mod_folder(mod_data))
        context_menu.add_command(label="📋 Copy Mod Name", 
                                command=lambda: self.copy_to_clipboard(mod_name))
        
        # Show menu at cursor position
        print(f"Showing menu at position: {event.x_root}, {event.y_root}")
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def open_mod_folder(self, mod_data):
        """Open the folder containing the mod file"""
        mod_folder = Path(mod_data['folder'])
        if mod_folder.exists():
            subprocess.Popen(f'explorer "{mod_folder}"')
        else:
            messagebox.showerror("Error", "Mod folder not found!")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", f"Copied to clipboard:\n{text}")
    
    def open_settings(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x250")
        settings_window.configure(bg="#1e1e1e")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Brickadia Paks Path
        tk.Label(
            settings_window,
            text="Brickadia Paks Folder:",
            bg="#2b2b2b",
            fg="#ffffff",
            font=("Arial", 10)
        ).pack(pady=(20, 5), padx=20, anchor="w")
        
        paks_frame = tk.Frame(settings_window, bg="#2b2b2b")
        paks_frame.pack(padx=20, fill=tk.X)
        
        paks_entry = tk.Entry(paks_frame, font=("Arial", 10), width=40)
        paks_entry.insert(0, self.config['Paths']['brickadia_paks'])
        paks_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def browse_paks():
            folder = filedialog.askdirectory(title="Select Brickadia Paks Folder")
            if folder:
                paks_entry.delete(0, tk.END)
                paks_entry.insert(0, folder)
        
        tk.Button(
            paks_frame,
            text="Browse",
            command=browse_paks,
            bg="#444444",
            fg="#ffffff",
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)
        
        # Mods Storage Path
        tk.Label(
            settings_window,
            text="Mods Storage Folder:",
            bg="#2b2b2b",
            fg="#ffffff",
            font=("Arial", 10)
        ).pack(pady=(20, 5), padx=20, anchor="w")
        
        storage_frame = tk.Frame(settings_window, bg="#2b2b2b")
        storage_frame.pack(padx=20, fill=tk.X)
        
        storage_entry = tk.Entry(storage_frame, font=("Arial", 10), width=40)
        storage_entry.insert(0, self.config['Paths']['mods_storage'])
        storage_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def browse_storage():
            folder = filedialog.askdirectory(title="Select Mods Storage Folder")
            if folder:
                storage_entry.delete(0, tk.END)
                storage_entry.insert(0, folder)
        
        tk.Button(
            storage_frame,
            text="Browse",
            command=browse_storage,
            bg="#444444",
            fg="#ffffff",
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)
        
        # Save button
        def save_settings():
            self.config['Paths']['brickadia_paks'] = paks_entry.get()
            self.config['Paths']['mods_storage'] = storage_entry.get()
            self.save_config()
            
            # Create mods storage directory if it doesn't exist
            os.makedirs(self.config['Paths']['mods_storage'], exist_ok=True)
            self.mods_storage_path = self.config['Paths']['mods_storage']
            
            messagebox.showinfo("Success", "Settings saved!")
            settings_window.destroy()
        
        tk.Button(
            settings_window,
            text="Save Settings",
            command=save_settings,
            bg="#0066cc",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(pady=20)
    
    def is_brickadia_running(self):
        """Check if Brickadia is currently running"""
        import psutil
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'brickadia' in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False
    
    def close_brickadia(self):
        """Close Brickadia if it's running"""
        import psutil
        closed = False
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'brickadia' in proc.info['name'].lower():
                    proc.terminate()  # Graceful shutdown
                    closed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if closed:
            # Wait a moment for the process to close
            import time
            time.sleep(2)
        
        return closed
    
    def restart_game_with_changes(self):
        """Close game, apply changes, and relaunch"""
        if not self.is_brickadia_running():
            messagebox.showinfo(
                "Game Not Running",
                "Brickadia is not currently running.\n\n"
                "Your mod changes have been applied.\n"
                "Click 'Launch Game' to start Brickadia."
            )
            return
        
        result = messagebox.askquestion(
            "Restart Game",
            "This will close Brickadia and relaunch it with your current mod configuration.\n\n"
            "Any unsaved progress in the game will be lost.\n\n"
            "Continue?",
            icon='warning'
        )
        
        if result == 'yes':
            # Close the game
            messagebox.showinfo(
                "Closing Game",
                "Closing Brickadia...\n\n"
                "The game will restart automatically."
            )
            
            if self.close_brickadia():
                # Launch game after closing
                self.launch_brickadia()
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to close Brickadia.\n\n"
                    "Please close it manually and click 'Launch Game'."
                )
    
    def launch_brickadia(self):
        """Launch Brickadia game"""
        try:
            # Brickadia requires special Steam setup - open Steam library page instead
            # This avoids license/authentication issues
            
            result = messagebox.askquestion(
                "Launch Brickadia",
                "Open Brickadia in your Steam library?\n\n"
                "This will open Steam to the Brickadia page where you can click PLAY.\n\n"
                "Note: Due to Brickadia's Steam setup, it must be launched\n"
                "directly from Steam to avoid authentication errors.",
                icon='question'
            )
            
            if result == 'yes':
                try:
                    # Open Steam library filtered to Brickadia
                    webbrowser.open('steam://nav/games/details/1386740')
                    messagebox.showinfo(
                        "Info", 
                        "Steam should now open to Brickadia.\n\n"
                        "Click the green PLAY button to launch the game."
                    )
                except Exception as e:
                    # Fallback - open Steam library home
                    try:
                        webbrowser.open('steam://open/games')
                        messagebox.showinfo(
                            "Info",
                            "Steam library opened.\n\n"
                            "Please find Brickadia and click PLAY to launch it."
                        )
                    except:
                        messagebox.showerror(
                            "Error",
                            "Could not open Steam.\n\n"
                            "Please launch Brickadia manually from your Steam library."
                        )
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Steam:\n{str(e)}")
    
    def filter_mods(self):
        """Filter mods based on search and filter criteria"""
        search_text = self.search_var.get().lower()
        filter_status = self.filter_var.get()
        
        # Clear existing items
        for item in self.mod_tree.get_children():
            self.mod_tree.delete(item)
        
        # Clear old icons
        self.mod_icons.clear()
        
        # Count for display
        filtered_count = 0
        
        # Add filtered mods
        for mod_id, mod in self.mods.items():
            # Apply status filter
            if filter_status == "Enabled Only" and not mod['enabled']:
                continue
            elif filter_status == "Disabled Only" and mod['enabled']:
                continue
            
            # Apply search filter
            if search_text:
                searchable = f"{mod['name']} {mod.get('description', '')} {mod.get('author', '')}".lower()
                if search_text not in searchable:
                    continue
            
            # Add mod to list
            status = "✓ Enabled" if mod['enabled'] else "✗ Disabled"
            
            # Add mod type badge to name
            mod_type = mod.get('mod_type', 'PAK')  # Default to PAK for backward compatibility
            mod_name = f"[{mod_type}] {mod['name']}"
            
            info_parts = []
            if mod.get('description'):
                info_parts.append(mod['description'])
            if mod.get('author'):
                info_parts.append(f"by {mod['author']}")
            if mod.get('version'):
                info_parts.append(f"v{mod['version']}")
            
            info_text = " | ".join(info_parts) if info_parts else ""
            
            # Load icon if available, or use fallback
            icon_image = None
            icon_path = mod.get('icon', '')
            if icon_path and Path(icon_path).exists():
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(icon_path)
                    img = img.resize((48, 48), Image.Resampling.LANCZOS)
                    icon_image = ImageTk.PhotoImage(img)
                    self.mod_icons[mod_id] = icon_image
                except Exception as e:
                    print(f"Failed to load icon for {mod['name']}: {e}")
            
            # If no icon loaded, use program logo as fallback
            if not icon_image:
                icon_image = self.get_fallback_icon_for_tree(mod_id)
            
            self.mod_tree.insert("", tk.END, iid=mod_id, image=icon_image if icon_image else "", 
                               values=(mod_name, status, info_text))
            filtered_count += 1
        
        # Update mod count label
        total_count = len(self.mods)
        if filtered_count == total_count:
            self.mod_count_label.config(text=f"({total_count} mods)")
        else:
            self.mod_count_label.config(text=f"({filtered_count} of {total_count} mods)")
    
    def enable_all_mods(self):
        """Enable all installed mods"""
        confirm = messagebox.askyesno(
            "Enable All Mods",
            f"Enable all {len(self.mods)} mods?\n\nThis may take a moment."
        )
        if not confirm:
            return
        
        enabled_count = 0
        for mod_id, mod in self.mods.items():
            if not mod['enabled']:
                try:
                    self.enable_mod(mod_id)
                    enabled_count += 1
                except Exception as e:
                    print(f"Failed to enable {mod['name']}: {e}")
        
        self.refresh_mod_list()
        messagebox.showinfo("Success", f"Enabled {enabled_count} mod(s)")
    
    def disable_all_mods(self):
        """Disable all installed mods"""
        confirm = messagebox.askyesno(
            "Disable All Mods",
            f"Disable all enabled mods?\n\nThis may take a moment."
        )
        if not confirm:
            return
        
        disabled_count = 0
        for mod_id, mod in self.mods.items():
            if mod['enabled']:
                try:
                    self.disable_mod(mod_id)
                    disabled_count += 1
                except Exception as e:
                    print(f"Failed to disable {mod['name']}: {e}")
        
        self.refresh_mod_list()
        messagebox.showinfo("Success", f"Disabled {disabled_count} mod(s)")
    
    def open_profiles(self):
        """Open mod profiles manager"""
        profiles_window = tk.Toplevel(self.root)
        profiles_window.title("Mod Profiles")
        profiles_window.geometry("600x500")
        profiles_window.configure(bg="#2b2b2b")
        profiles_window.transient(self.root)
        
        # Title
        tk.Label(
            profiles_window,
            text="Mod Profiles",
            font=("Arial", 16, "bold"),
            bg="#2b2b2b",
            fg="#ffffff"
        ).pack(pady=10)
        
        tk.Label(
            profiles_window,
            text="Save and load different mod configurations",
            font=("Arial", 10),
            bg="#2b2b2b",
            fg="#888888"
        ).pack(pady=5)
        
        # Profiles list
        list_frame = tk.Frame(profiles_window, bg="#2b2b2b")
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        profiles_listbox = tk.Listbox(
            list_frame,
            bg="#3c3c3c",
            fg="#ffffff",
            font=("Arial", 11),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        profiles_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=profiles_listbox.yview)
        
        # Load profiles
        profiles_file = Path("profiles.json")
        profiles = {}
        if profiles_file.exists():
            try:
                with open(profiles_file, 'r') as f:
                    profiles = json.load(f)
            except:
                pass
        
        def refresh_profiles_list():
            profiles_listbox.delete(0, tk.END)
            for profile_name in profiles.keys():
                enabled_count = len([m for m in profiles[profile_name] if m in self.mods])
                profiles_listbox.insert(tk.END, f"{profile_name} ({enabled_count} mods)")
        
        refresh_profiles_list()
        
        # Buttons frame
        btn_frame = tk.Frame(profiles_window, bg="#2b2b2b")
        btn_frame.pack(pady=10)
        
        def save_profile():
            profile_name = tk.simpledialog.askstring("Save Profile", "Enter profile name:", parent=profiles_window)
            if profile_name:
                # Save list of enabled mod IDs
                enabled_mods = [mod_id for mod_id, mod in self.mods.items() if mod['enabled']]
                profiles[profile_name] = enabled_mods
                
                with open(profiles_file, 'w') as f:
                    json.dump(profiles, f, indent=2)
                
                refresh_profiles_list()
                messagebox.showinfo("Success", f"Profile '{profile_name}' saved with {len(enabled_mods)} mod(s)")
        
        def load_profile():
            selection = profiles_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a profile to load")
                return
            
            profile_name = list(profiles.keys())[selection[0]]
            enabled_mods = profiles[profile_name]
            
            confirm = messagebox.askyesno(
                "Load Profile",
                f"Load profile '{profile_name}'?\n\nThis will:\n"
                f"• Disable all currently enabled mods\n"
                f"• Enable {len(enabled_mods)} mod(s) from this profile"
            )
            if not confirm:
                return
            
            # Disable all mods first
            for mod_id in self.mods:
                if self.mods[mod_id]['enabled']:
                    self.disable_mod(mod_id)
            
            # Enable mods from profile
            enabled_count = 0
            for mod_id in enabled_mods:
                if mod_id in self.mods:
                    self.enable_mod(mod_id)
                    enabled_count += 1
            
            self.refresh_mod_list()
            messagebox.showinfo("Success", f"Loaded profile '{profile_name}' ({enabled_count} mods enabled)")
            profiles_window.destroy()
        
        def delete_profile():
            selection = profiles_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a profile to delete")
                return
            
            profile_name = list(profiles.keys())[selection[0]]
            confirm = messagebox.askyesno("Delete Profile", f"Delete profile '{profile_name}'?")
            if confirm:
                del profiles[profile_name]
                with open(profiles_file, 'w') as f:
                    json.dump(profiles, f, indent=2)
                refresh_profiles_list()
                messagebox.showinfo("Success", f"Profile '{profile_name}' deleted")
        
        tk.Button(
            btn_frame,
            text="💾 Save Current",
            command=save_profile,
            bg="#00aa00",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="📂 Load Profile",
            command=load_profile,
            bg="#0066cc",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🗑️ Delete",
            command=delete_profile,
            bg="#aa0000",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def open_paks_folder(self):
        """Open the Paks folder in File Explorer"""
        paks_path = Path(self.config['Paths']['brickadia_paks'])
        
        if not paks_path.exists():
            messagebox.showerror(
                "Folder Not Found",
                f"The Paks folder does not exist:\n{paks_path}\n\n"
                "Please make sure Brickadia is properly installed."
            )
            return
        
        try:
            # Open the folder in Windows Explorer
            import subprocess
            subprocess.Popen(f'explorer "{paks_path}"')
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to open Paks folder:\n{str(e)}"
            )
    
    def open_about(self):
        """Show About dialog with version info and update check"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Brickadia Mod Loader")
        about_window.geometry("450x350")
        about_window.configure(bg="#1e1e1e")
        about_window.transient(self.root)
        about_window.resizable(False, False)
        
        # Center the window
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (about_window.winfo_width() // 2)
        y = (about_window.winfo_screenheight() // 2) - (about_window.winfo_height() // 2)
        about_window.geometry(f"+{x}+{y}")
        
        # Logo if available
        if hasattr(self, 'logo_ui_photo') and self.logo_ui_photo:
            logo_label = tk.Label(about_window, image=self.logo_ui_photo, bg="#1e1e1e")
            logo_label.pack(pady=(20, 10))
        
        # Title
        tk.Label(
            about_window,
            text="Brickadia Mod Loader",
            font=("Segoe UI", 18, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        ).pack(pady=(10, 5))
        
        # Version
        tk.Label(
            about_window,
            text=f"Version {self.VERSION}",
            font=("Segoe UI", 11),
            bg="#1e1e1e",
            fg="#888888"
        ).pack(pady=5)
        
        # Description
        tk.Label(
            about_window,
            text="A modern mod manager for Brickadia",
            font=("Segoe UI", 10),
            bg="#1e1e1e",
            fg="#ffffff"
        ).pack(pady=10)
        
        # Separator
        tk.Frame(about_window, bg="#404040", height=1).pack(fill=tk.X, padx=40, pady=15)
        
        # Buttons frame
        btn_frame = tk.Frame(about_window, bg="#1e1e1e")
        btn_frame.pack(pady=10)
        
        # Check for Updates button
        tk.Button(
            btn_frame,
            text="🔄 Check for Updates",
            command=lambda: [about_window.destroy(), self.check_for_updates()],
            bg=self.THEME_ACCENT,
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            activebackground=self.THEME_ACCENT_HOVER
        ).pack(side=tk.LEFT, padx=5)
        
        # GitHub button
        tk.Button(
            btn_frame,
            text="🌐 View on GitHub",
            command=lambda: webbrowser.open("https://github.com/Inxects1/BrickadiaModLoader"),
            bg="#3a3a3a",
            fg=self.THEME_TEXT,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            activebackground="#4a4a4a"
        ).pack(side=tk.LEFT, padx=5)
        
        # Footer
        tk.Label(
            about_window,
            text="Made with ❤️ for the Brickadia community",
            font=("Segoe UI", 9),
            bg="#1e1e1e",
            fg="#666666"
        ).pack(side=tk.BOTTOM, pady=20)
    
    def open_game_settings(self):
        """Open GameUserSettings.ini editor"""
        # Find GameUserSettings.ini path
        user_home = Path.home()
        settings_path = user_home / "AppData" / "Local" / "Brickadia" / "Saved" / "Config" / "Windows" / "GameUserSettings.ini"
        
        if not settings_path.exists():
            # Try to create the directory structure
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            messagebox.showwarning(
                "Settings File Not Found",
                f"GameUserSettings.ini not found at:\n{settings_path}\n\n"
                "The file will be created when you launch Brickadia for the first time.\n"
                "You can still create and edit it here."
            )
        
        # Create settings editor window
        settings_editor = tk.Toplevel(self.root)
        settings_editor.title("Brickadia Game Settings")
        settings_editor.geometry("800x600")
        settings_editor.configure(bg="#2b2b2b")
        settings_editor.transient(self.root)
        
        # Title
        tk.Label(
            settings_editor,
            text="GameUserSettings.ini Editor",
            font=("Arial", 16, "bold"),
            bg="#2b2b2b",
            fg="#ffffff"
        ).pack(pady=10)
        
        # Path label
        tk.Label(
            settings_editor,
            text=f"File: {settings_path}",
            font=("Arial", 9),
            bg="#2b2b2b",
            fg="#888888"
        ).pack(pady=5)
        
        # Text editor frame
        editor_frame = tk.Frame(settings_editor, bg="#2b2b2b")
        editor_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(editor_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget
        text_editor = tk.Text(
            editor_frame,
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="#ffffff",
            font=("Consolas", 10),
            yscrollcommand=scrollbar.set,
            wrap=tk.NONE
        )
        text_editor.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_editor.yview)
        
        # Load existing content if file exists
        if settings_path.exists():
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    text_editor.insert('1.0', content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read settings file:\n{str(e)}")
        else:
            # Insert default template
            default_content = """; Brickadia Game User Settings
; Edit with caution - incorrect values may cause issues

[/Script/Engine.GameUserSettings]
ResolutionSizeX=1920
ResolutionSizeY=1080
WindowPosX=0
WindowPosY=0
FullscreenMode=1
LastUserConfirmedResolutionSizeX=1920
LastUserConfirmedResolutionSizeY=1080
bUseVSync=False
"""
            text_editor.insert('1.0', default_content)
        
        # Buttons frame
        buttons_frame = tk.Frame(settings_editor, bg="#2b2b2b")
        buttons_frame.pack(pady=10)
        
        def save_game_settings():
            try:
                content = text_editor.get('1.0', tk.END)
                # Remove trailing newline that tkinter adds
                content = content.rstrip('\n')
                
                # Create directory if it doesn't exist
                settings_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo("Success", "Game settings saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings:\n{str(e)}")
        
        def open_in_notepad():
            try:
                if settings_path.exists():
                    os.startfile(settings_path)
                else:
                    messagebox.showwarning("File Not Found", "Please save the file first before opening in external editor.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open in notepad:\n{str(e)}")
        
        # Save button
        tk.Button(
            buttons_frame,
            text="💾 Save Settings",
            command=save_game_settings,
            bg="#00aa00",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Open in Notepad button
        tk.Button(
            buttons_frame,
            text="📝 Open in Notepad",
            command=open_in_notepad,
            bg="#0066cc",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Close button
        tk.Button(
            buttons_frame,
            text="Close",
            command=settings_editor.destroy,
            bg="#666666",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)


def main():
    root = TkinterDnD.Tk()
    app = BrickadiaModLoader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
