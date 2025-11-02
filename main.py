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
    VERSION = "3.0.0"
    GITHUB_REPO = "Inxects1/BrickadiaModLoader"
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"Brickadia Mod Loader v{self.VERSION}")
        self.root.geometry("1400x1000")
        self.root.minsize(1300, 950)
        self.root.configure(bg="#1e1e1e")
        
        # Load and set window icon
        try:
            from PIL import Image, ImageTk
            # Get the correct path for the logo (works for both script and exe)
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                application_path = sys._MEIPASS
            else:
                # Running as script
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            logo_path = Path(application_path) / "logo.png"
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
        
        # Configuration
        self.config_file = "config.ini"
        self.mods_data_file = "mods.json"
        self.load_config()
        
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
            self.save_config()
        
        # Create mods storage directory if it doesn't exist
        self.mods_storage_path = self.config['Paths']['mods_storage']
        os.makedirs(self.mods_storage_path, exist_ok=True)
        
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
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
        setup_window.configure(bg="#1e1e1e")
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
        top_bar = tk.Frame(self.root, bg="#252525", height=70)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)
        
        # Title section (left) with logo
        title_section = tk.Frame(top_bar, bg="#252525")
        title_section.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Create horizontal layout for logo and text
        title_inner = tk.Frame(title_section, bg="#252525")
        title_inner.pack(anchor="w")
        
        # Logo on the left
        if hasattr(self, 'logo_ui_photo') and self.logo_ui_photo:
            logo_label = tk.Label(
                title_inner,
                image=self.logo_ui_photo,
                bg="#252525"
            )
            logo_label.pack(side=tk.LEFT, padx=(0, 12))
        
        # Text on the right
        text_frame = tk.Frame(title_inner, bg="#252525")
        text_frame.pack(side=tk.LEFT)
        
        title_label = tk.Label(
            text_frame, 
            text="Brickadia Mod Loader", 
            font=("Segoe UI", 18, "bold"),
            bg="#252525",
            fg="#ffffff"
        )
        title_label.pack(anchor="w")
        
        version_label = tk.Label(
            text_frame,
            text=f"v{self.VERSION}",
            font=("Segoe UI", 9),
            bg="#252525",
            fg="#888888"
        )
        version_label.pack(anchor="w")
        
        # Action buttons (right side of top bar)
        actions_frame = tk.Frame(top_bar, bg="#252525")
        actions_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Launch button (prominent)
        launch_btn = tk.Button(
            actions_frame,
            text="🚀 Launch Game",
            command=self.launch_brickadia,
            bg="#4CAF50",
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=25,
            pady=12,
            cursor="hand2",
            activebackground="#45a049"
        )
        launch_btn.pack(side=tk.RIGHT, padx=5)
        
        # Settings button
        settings_btn = tk.Button(
            actions_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            bg="#3a3a3a",
            fg="#ffffff",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=12,
            cursor="hand2",
            activebackground="#4a4a4a"
        )
        settings_btn.pack(side=tk.RIGHT, padx=5)
        
        # Game Settings button
        game_settings_btn = tk.Button(
            actions_frame,
            text="🎮 Game Settings",
            command=self.open_game_settings,
            bg="#3a3a3a",
            fg="#ffffff",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=12,
            cursor="hand2",
            activebackground="#4a4a4a"
        )
        game_settings_btn.pack(side=tk.RIGHT, padx=5)
        
        # ===== MAIN CONTENT AREA =====
        main_content = tk.Frame(self.root, bg="#1e1e1e")
        main_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left side - Mod Library (wider)
        left_panel = tk.Frame(main_content, bg="#1e1e1e")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Drop zone (compact, modern design)
        drop_frame = tk.Frame(left_panel, bg="#2d2d2d", relief=tk.FLAT, bd=0, highlightthickness=2, highlightbackground="#3a3a3a")
        drop_frame.pack(fill=tk.X, pady=(0, 15))
        
        drop_inner = tk.Frame(drop_frame, bg="#2d2d2d")
        drop_inner.pack(padx=20, pady=15)
        
        tk.Label(
            drop_inner,
            text="📦",
            font=("Segoe UI", 24),
            bg="#2d2d2d",
            fg="#ffffff"
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        drop_text_frame = tk.Frame(drop_inner, bg="#2d2d2d")
        drop_text_frame.pack(side=tk.LEFT)
        
        self.drop_label = tk.Label(
            drop_text_frame,
            text="Drop mod files here to install",
            font=("Segoe UI", 12, "bold"),
            bg="#2d2d2d",
            fg="#ffffff"
        )
        self.drop_label.pack(anchor="w")
        
        tk.Label(
            drop_text_frame,
            text="Supports .zip, .rar, .7z, and .pak files",
            font=("Segoe UI", 9),
            bg="#2d2d2d",
            fg="#888888"
        ).pack(anchor="w")
        
        # Browse button
        browse_btn = tk.Button(
            drop_inner,
            text="📁 Browse",
            command=self.browse_archive,
            bg="#4CAF50",
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            activebackground="#45a049"
        )
        browse_btn.pack(side=tk.LEFT, padx=(15, 0))
        
        # Enable drag and drop
        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        
        # Mod library header with search
        library_header = tk.Frame(left_panel, bg="#252525", height=50)
        library_header.pack(fill=tk.X, pady=(0, 10))
        library_header.pack_propagate(False)
        
        # Left side - title and count
        header_left = tk.Frame(library_header, bg="#252525")
        header_left.pack(side=tk.LEFT, padx=15, pady=10)
        
        list_label = tk.Label(
            header_left,
            text="📚 Mod Library",
            font=("Segoe UI", 14, "bold"),
            bg="#252525",
            fg="#ffffff"
        )
        list_label.pack(side=tk.LEFT)
        
        self.mod_count_label = tk.Label(
            header_left,
            text="(0 mods)",
            font=("Segoe UI", 10),
            bg="#252525",
            fg="#888888"
        )
        self.mod_count_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Right side - search and filter
        header_right = tk.Frame(library_header, bg="#252525")
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
                 background=[('selected', '#4CAF50')],
                 foreground=[('selected', '#ffffff')])
        
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
        
        # Store for icon images (prevent garbage collection)
        self.mod_icons = {}
        
        # Right side - Mod Load Order
        right_panel = tk.Frame(main_content, bg="#252525", width=280)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Load order header
        order_header = tk.Frame(right_panel, bg="#252525")
        order_header.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            order_header,
            text="🔢 Load Order",
            font=("Segoe UI", 12, "bold"),
            bg="#252525",
            fg="#ffffff"
        ).pack(anchor="w")
        
        tk.Label(
            order_header,
            text="Drag mods to reorder",
            font=("Segoe UI", 9),
            bg="#252525",
            fg="#888888"
        ).pack(anchor="w")
        
        # Load order list
        order_frame = tk.Frame(right_panel, bg="#2d2d2d")
        order_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        order_scroll = ttk.Scrollbar(order_frame)
        order_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.order_listbox = tk.Listbox(
            order_frame,
            bg="#2d2d2d",
            fg="#ffffff",
            font=("Segoe UI", 9),
            selectbackground="#4CAF50",
            selectforeground="#ffffff",
            bd=0,
            highlightthickness=0,
            yscrollcommand=order_scroll.set
        )
        self.order_listbox.pack(fill=tk.BOTH, expand=True)
        order_scroll.config(command=self.order_listbox.yview)
        
        # Order control buttons
        order_btn_frame = tk.Frame(right_panel, bg="#252525")
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
        bottom_bar = tk.Frame(self.root, bg="#252525", height=65)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)
        bottom_bar.pack_propagate(False)
        
        btn_frame = tk.Frame(bottom_bar, bg="#252525")
        btn_frame.pack(pady=12)
        
        # Mod actions
        tk.Label(
            btn_frame,
            text="Selected Mod:",
            font=("Segoe UI", 9, "bold"),
            bg="#252525",
            fg="#888888"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="✓ Enable",
            command=self.enable_selected_mod,
            bg="#4CAF50",
            fg="#ffffff",
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
            bg="#FF9800",
            fg="#ffffff",
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
            bg="#f44336",
            fg="#ffffff",
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
            bg="#252525",
            fg="#888888"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="✓ All",
            command=self.enable_all_mods,
            bg="#2e7d32",
            fg="#ffffff",
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
            fg="#ffffff",
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
            bg="#9C27B0",
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            activebackground="#7B1FA2"
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
            
            # Find all .pak files in extracted content
            pak_files = list(temp_extract.rglob("*.pak"))
            
            if not pak_files:
                messagebox.showerror("Error", "No .pak files found in the archive!")
                shutil.rmtree(temp_extract)
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
        """Enable a mod by copying all its files to Brickadia paks folder"""
        mod = self.mods[mod_id]
        
        if mod['enabled']:
            messagebox.showinfo("Info", f"{mod['name']} is already enabled")
            return
        
        try:
            mod_folder = Path(mod['folder'])
            game_paks = Path(self.config['Paths']['brickadia_paks'])
            
            if not mod_folder.exists():
                messagebox.showerror("Error", f"Mod folder not found:\n{mod_folder}")
                return
            
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
            # Remove all mod files from game directory
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
    
    def update_load_order_list(self):
        """Update the load order listbox with enabled mods"""
        self.order_listbox.delete(0, tk.END)
        
        # Get all enabled mods sorted by load order
        enabled_mods = [(mod_id, mod) for mod_id, mod in self.mods.items() if mod['enabled']]
        enabled_mods.sort(key=lambda x: x[1].get('load_order', 999))
        
        for mod_id, mod in enabled_mods:
            self.order_listbox.insert(tk.END, mod['name'])
            # Store mod_id in listbox item data (for future use)
    
    def move_mod_up(self):
        """Move selected mod up in load order"""
        selection = self.order_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        idx = selection[0]
        # Get the text values
        text = self.order_listbox.get(idx)
        
        # Delete and reinsert one position up
        self.order_listbox.delete(idx)
        self.order_listbox.insert(idx - 1, text)
        self.order_listbox.selection_set(idx - 1)
        
        # TODO: Update actual load order in mods data
        messagebox.showinfo("Info", "Mod load order feature coming soon!\n\nThis will control the order mods are loaded in-game.")
    
    def move_mod_down(self):
        """Move selected mod down in load order"""
        selection = self.order_listbox.curselection()
        if not selection or selection[0] == self.order_listbox.size() - 1:
            return
        
        idx = selection[0]
        # Get the text values
        text = self.order_listbox.get(idx)
        
        # Delete and reinsert one position down
        self.order_listbox.delete(idx)
        self.order_listbox.insert(idx + 1, text)
        self.order_listbox.selection_set(idx + 1)
        
        # TODO: Update actual load order in mods data
        messagebox.showinfo("Info", "Mod load order feature coming soon!\n\nThis will control the order mods are loaded in-game.")
    
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
            
            info_parts = []
            if mod.get('description'):
                info_parts.append(mod['description'])
            if mod.get('author'):
                info_parts.append(f"by {mod['author']}")
            if mod.get('version'):
                info_parts.append(f"v{mod['version']}")
            
            info_text = " | ".join(info_parts) if info_parts else ""
            
            # Load icon if available
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
            
            self.mod_tree.insert("", tk.END, iid=mod_id, image=icon_image if icon_image else "", 
                               values=(mod['name'], status, info_text))
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
