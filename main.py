import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import shutil
import zipfile
import rarfile
from pathlib import Path
from tkinterdnd2 import DND_FILES, TkinterDnD
import configparser


class BrickadiaModLoader:
    def __init__(self, root):
        self.root = root
        self.root.title("Brickadia Mod Loader")
        self.root.geometry("800x600")
        self.root.configure(bg="#2b2b2b")
        
        # Configuration
        self.config_file = "config.ini"
        self.mods_data_file = "mods.json"
        self.load_config()
        
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
        """Create the GUI widgets"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="Brickadia Mod Loader", 
            font=("Arial", 20, "bold"),
            bg="#2b2b2b",
            fg="#ffffff"
        )
        title_label.pack(pady=10)
        
        # Settings button
        settings_btn = tk.Button(
            self.root,
            text="⚙ Settings",
            command=self.open_settings,
            bg="#444444",
            fg="#ffffff",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        settings_btn.pack(anchor="ne", padx=10, pady=5)
        
        # Drop zone
        drop_frame = tk.Frame(self.root, bg="#3c3c3c", relief=tk.RAISED, bd=2)
        drop_frame.pack(pady=20, padx=20, fill=tk.X)
        
        self.drop_label = tk.Label(
            drop_frame,
            text="📦 Drag & Drop .zip or .rar files here to install mods",
            font=("Arial", 12),
            bg="#3c3c3c",
            fg="#aaaaaa",
            pady=30
        )
        self.drop_label.pack(fill=tk.BOTH, expand=True)
        
        # Enable drag and drop
        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        
        # Browse button
        browse_btn = tk.Button(
            self.root,
            text="Browse for Archive",
            command=self.browse_archive,
            bg="#0066cc",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        browse_btn.pack(pady=5)
        
        # Mod list frame
        list_frame = tk.Frame(self.root, bg="#2b2b2b")
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        list_label = tk.Label(
            list_frame,
            text="Installed Mods",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#ffffff"
        )
        list_label.pack(anchor="w", pady=5)
        
        # Treeview for mods
        tree_frame = tk.Frame(list_frame, bg="#2b2b2b")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                       background="#3c3c3c",
                       foreground="white",
                       rowheight=25,
                       fieldbackground="#3c3c3c")
        style.configure("Treeview.Heading",
                       background="#444444",
                       foreground="white",
                       relief=tk.FLAT)
        style.map('Treeview', background=[('selected', '#0066cc')])
        
        self.mod_tree = ttk.Treeview(
            tree_frame,
            columns=("Name", "Status", "File"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        self.mod_tree.heading("Name", text="Mod Name")
        self.mod_tree.heading("Status", text="Status")
        self.mod_tree.heading("File", text="File Name")
        
        self.mod_tree.column("Name", width=300)
        self.mod_tree.column("Status", width=100)
        self.mod_tree.column("File", width=300)
        
        self.mod_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.mod_tree.yview)
        
        # Buttons frame
        btn_frame = tk.Frame(self.root, bg="#2b2b2b")
        btn_frame.pack(pady=10)
        
        enable_btn = tk.Button(
            btn_frame,
            text="Enable Mod",
            command=self.enable_selected_mod,
            bg="#00aa00",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        enable_btn.pack(side=tk.LEFT, padx=5)
        
        disable_btn = tk.Button(
            btn_frame,
            text="Disable Mod",
            command=self.disable_selected_mod,
            bg="#aa6600",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        disable_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(
            btn_frame,
            text="Delete Mod",
            command=self.delete_selected_mod,
            bg="#aa0000",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
    
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
                with rarfile.RarFile(archive_path, 'r') as rar_ref:
                    rar_ref.extractall(temp_extract)
            
            # Find all .pak files in extracted content
            pak_files = list(temp_extract.rglob("*.pak"))
            
            if not pak_files:
                messagebox.showerror("Error", "No .pak files found in the archive!")
                shutil.rmtree(temp_extract)
                return
            
            # Move pak files to mods storage
            for pak_file in pak_files:
                mod_name = pak_file.stem
                destination = Path(self.mods_storage_path) / pak_file.name
                
                # If file exists, add number suffix
                counter = 1
                while destination.exists():
                    destination = Path(self.mods_storage_path) / f"{mod_name}_{counter}.pak"
                    counter += 1
                
                shutil.copy2(pak_file, destination)
                
                # Add to mods database
                self.mods[destination.name] = {
                    'name': mod_name,
                    'file': destination.name,
                    'enabled': False,
                    'storage_path': str(destination)
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
            values = self.mod_tree.item(item, 'values')
            file_name = values[2]
            
            if file_name in self.mods:
                self.enable_mod(file_name)
        
        self.refresh_mod_list()
    
    def disable_selected_mod(self):
        """Disable the selected mod"""
        selection = self.mod_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mod to disable")
            return
        
        for item in selection:
            values = self.mod_tree.item(item, 'values')
            file_name = values[2]
            
            if file_name in self.mods:
                self.disable_mod(file_name)
        
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
            values = self.mod_tree.item(item, 'values')
            file_name = values[2]
            
            if file_name in self.mods:
                self.delete_mod(file_name)
        
        self.refresh_mod_list()
    
    def enable_mod(self, file_name):
        """Enable a mod by moving it to Brickadia paks folder"""
        mod = self.mods[file_name]
        
        if mod['enabled']:
            messagebox.showinfo("Info", f"{mod['name']} is already enabled")
            return
        
        try:
            source = Path(mod['storage_path'])
            destination = Path(self.config['Paths']['brickadia_paks']) / file_name
            
            if not source.exists():
                messagebox.showerror("Error", f"Mod file not found:\n{source}")
                return
            
            shutil.copy2(source, destination)
            mod['enabled'] = True
            mod['game_path'] = str(destination)
            self.save_mods()
            
            messagebox.showinfo("Success", f"Enabled: {mod['name']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enable mod:\n{str(e)}")
    
    def disable_mod(self, file_name):
        """Disable a mod by removing it from Brickadia paks folder"""
        mod = self.mods[file_name]
        
        if not mod['enabled']:
            messagebox.showinfo("Info", f"{mod['name']} is already disabled")
            return
        
        try:
            game_path = Path(mod.get('game_path', ''))
            
            if game_path.exists():
                os.remove(game_path)
            
            mod['enabled'] = False
            if 'game_path' in mod:
                del mod['game_path']
            self.save_mods()
            
            messagebox.showinfo("Success", f"Disabled: {mod['name']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disable mod:\n{str(e)}")
    
    def delete_mod(self, file_name):
        """Delete a mod completely"""
        mod = self.mods[file_name]
        
        try:
            # Disable first if enabled
            if mod['enabled']:
                self.disable_mod(file_name)
            
            # Delete from storage
            storage_path = Path(mod['storage_path'])
            if storage_path.exists():
                os.remove(storage_path)
            
            # Remove from database
            del self.mods[file_name]
            self.save_mods()
            
            messagebox.showinfo("Success", f"Deleted: {mod['name']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete mod:\n{str(e)}")
    
    def refresh_mod_list(self):
        """Refresh the mod list display"""
        # Clear existing items
        for item in self.mod_tree.get_children():
            self.mod_tree.delete(item)
        
        # Add mods
        for file_name, mod in self.mods.items():
            status = "✓ Enabled" if mod['enabled'] else "✗ Disabled"
            self.mod_tree.insert("", tk.END, values=(mod['name'], status, file_name))
    
    def open_settings(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x250")
        settings_window.configure(bg="#2b2b2b")
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


def main():
    root = TkinterDnD.Tk()
    app = BrickadiaModLoader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
