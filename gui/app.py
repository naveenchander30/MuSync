import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
from pathlib import Path
import threading
import webbrowser

# Add parent directory to path for imports when running standalone
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.state import SyncState
from sync.spotify_import import import_spotify
from sync.spotify_export import export_spotify
from sync.ytmusic_import import import_ytmusic
from sync.ytmusic_export import export_ytmusic
from config import AUTH_SERVER


class MuSyncApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MuSync - Music Library Synchronization")
        self.geometry("1000x700")
        self.configure(bg="#1a1a1a")
        self.state = SyncState()
        self.is_running = False
        
        # Set theme colors
        self.colors = {
            "bg": "#1a1a1a",
            "fg": "#ffffff",
            "accent": "#1db954",  # Spotify green
            "secondary": "#ff0000",  # YouTube red
            "button": "#2a2a2a",
            "button_hover": "#3a3a3a",
            "text_bg": "#2d2d2d",
            "success": "#4caf50",
            "error": "#f44336",
            "warning": "#ff9800"
        }
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the complete UI layout"""
        # Create menu bar
        self._create_menu()
        
        # Main container with padding
        main_frame = tk.Frame(self, bg=self.colors["bg"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._create_header(main_frame)
        
        # Status section
        self._create_status_section(main_frame)
        
        # Control buttons section
        self._create_control_section(main_frame)
        
        # Progress section
        self._create_progress_section(main_frame)
        
        # Log section
        self._create_log_section(main_frame)
        
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self, bg=self.colors["button"], fg=self.colors["fg"])
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["button"], fg=self.colors["fg"])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Logs", command=self.clear_logs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # Auth menu
        auth_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["button"], fg=self.colors["fg"])
        menubar.add_cascade(label="Authentication", menu=auth_menu)
        auth_menu.add_command(label="Login to Spotify", command=self.open_spotify_auth)
        auth_menu.add_command(label="Login to YouTube Music", command=self.open_ytmusic_auth)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["button"], fg=self.colors["fg"])
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def _create_header(self, parent):
        """Create header with title and description"""
        header_frame = tk.Frame(parent, bg=self.colors["bg"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = tk.Label(
            header_frame,
            text="🎵 MuSync",
            font=("Segoe UI", 24, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent"]
        )
        title.pack()
        
        subtitle = tk.Label(
            header_frame,
            text="Sync your music library between Spotify and YouTube Music",
            font=("Segoe UI", 10),
            bg=self.colors["bg"],
            fg="#888888"
        )
        subtitle.pack()
        
    def _create_status_section(self, parent):
        """Create status indicator section"""
        status_frame = tk.Frame(parent, bg=self.colors["button"], relief="ridge", bd=2)
        status_frame.pack(fill="x", pady=(0, 20))
        
        inner_frame = tk.Frame(status_frame, bg=self.colors["button"])
        inner_frame.pack(fill="x", padx=15, pady=15)
        
        # Current operation status
        status_label = tk.Label(
            inner_frame,
            text="Status:",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["button"],
            fg=self.colors["fg"]
        )
        status_label.pack(side="left")
        
        self.status_text = tk.Label(
            inner_frame,
            text="Idle",
            font=("Segoe UI", 10),
            bg=self.colors["button"],
            fg=self.colors["accent"]
        )
        self.status_text.pack(side="left", padx=10)
        
        # Stats on the right
        stats_frame = tk.Frame(inner_frame, bg=self.colors["button"])
        stats_frame.pack(side="right")
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Added: 0 | Failed: 0",
            font=("Segoe UI", 10),
            bg=self.colors["button"],
            fg="#888888"
        )
        self.stats_label.pack()
        
    def _create_control_section(self, parent):
        """Create control buttons section"""
        control_frame = tk.Frame(parent, bg=self.colors["bg"])
        control_frame.pack(fill="x", pady=(0, 20))
        
        # Export section
        export_frame = tk.LabelFrame(
            control_frame,
            text="Export Playlists",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["button"],
            fg=self.colors["fg"],
            relief="ridge",
            bd=2
        )
        export_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        export_inner = tk.Frame(export_frame, bg=self.colors["button"])
        export_inner.pack(fill="both", expand=True, padx=15, pady=15)
        
        self._create_button(
            export_inner,
            "📥 Export from Spotify",
            self.export_spotify,
            self.colors["accent"]
        ).pack(fill="x", pady=5)
        
        self._create_button(
            export_inner,
            "📥 Export from YouTube Music",
            self.export_ytmusic,
            self.colors["secondary"]
        ).pack(fill="x", pady=5)
        
        # Import section
        import_frame = tk.LabelFrame(
            control_frame,
            text="Import Playlists",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["button"],
            fg=self.colors["fg"],
            relief="ridge",
            bd=2
        )
        import_frame.pack(side="left", fill="both", expand=True)
        
        import_inner = tk.Frame(import_frame, bg=self.colors["button"])
        import_inner.pack(fill="both", expand=True, padx=15, pady=15)
        
        self._create_button(
            import_inner,
            "📤 Import to Spotify",
            self.import_spotify,
            self.colors["accent"]
        ).pack(fill="x", pady=5)
        
        self._create_button(
            import_inner,
            "📤 Import to YouTube Music",
            self.import_ytmusic,
            self.colors["secondary"]
        ).pack(fill="x", pady=5)
        
    def _create_button(self, parent, text, command, color):
        """Create a styled button"""
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold"),
            bg=color,
            fg="#ffffff",
            activebackground=color,
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            height=2,
            bd=0
        )
        button.bind("<Enter>", lambda e: button.config(bg=self._lighten_color(color)))
        button.bind("<Leave>", lambda e: button.config(bg=color))
        return button
        
    def _lighten_color(self, color):
        """Lighten a hex color"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        return f'#{r:02x}{g:02x}{b:02x}'
        
    def _create_progress_section(self, parent):
        """Create progress bar section"""
        progress_frame = tk.Frame(parent, bg=self.colors["button"], relief="ridge", bd=2)
        progress_frame.pack(fill="x", pady=(0, 20))
        
        inner_frame = tk.Frame(progress_frame, bg=self.colors["button"])
        inner_frame.pack(fill="x", padx=15, pady=15)
        
        self.progress_label = tk.Label(
            inner_frame,
            text="Ready",
            font=("Segoe UI", 9),
            bg=self.colors["button"],
            fg="#888888"
        )
        self.progress_label.pack(anchor="w", pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(
            inner_frame,
            mode='indeterminate',
            length=300
        )
        self.progress_bar.pack(fill="x")
        
    def _create_log_section(self, parent):
        """Create log display section"""
        log_frame = tk.LabelFrame(
            parent,
            text="Activity Log",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["button"],
            fg=self.colors["fg"],
            relief="ridge",
            bd=2
        )
        log_frame.pack(fill="both", expand=True)
        
        log_inner = tk.Frame(log_frame, bg=self.colors["button"])
        log_inner.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log = scrolledtext.ScrolledText(
            log_inner,
            font=("Consolas", 9),
            bg=self.colors["text_bg"],
            fg=self.colors["fg"],
            wrap="word",
            relief="flat",
            insertbackground=self.colors["fg"]
        )
        self.log.pack(fill="both", expand=True)
        
        # Configure tags for colored output
        self.log.tag_config("success", foreground=self.colors["success"])
        self.log.tag_config("error", foreground=self.colors["error"])
        self.log.tag_config("warning", foreground=self.colors["warning"])
        self.log.tag_config("info", foreground="#2196f3")
        
    def log_message(self, message, tag=""):
        """Add a message to the log"""
        self.log.insert("end", message + "\n", tag)
        self.log.see("end")
    
    def check_authentication(self, service="spotify"):
        """Check if user is authenticated for a service"""
        try:
            import requests
            url = f"{AUTH_SERVER}/{service}/token"
            resp = requests.get(url, timeout=30)
            return resp.status_code == 200
        except Exception:
            return False
    
    def prompt_authentication(self, service="spotify"):
        """Prompt user to authenticate"""
        service_name = "Spotify" if service == "spotify" else "YouTube Music"
        response = messagebox.askyesno(
            "Authentication Required",
            f"You need to authenticate with {service_name} first.\n\n"
            f"Would you like to open the login page now?"
        )
        if response:
            if service == "spotify":
                self.open_spotify_auth()
            else:
                self.open_ytmusic_auth()
            messagebox.showinfo(
                "Complete Authentication",
                f"Please complete the {service_name} authentication in your browser, "
                f"then try the operation again."
            )
        return False
        
    def update_ui(self, state):
        """Update UI with current sync state"""
        if state.current_playlist:
            self.progress_label.config(text=f"Processing: {state.current_playlist}")
            self.log_message(f"⏳ Processing playlist: {state.current_playlist}", "info")
        
        self.stats_label.config(
            text=f"Added: {len(state.added)} | Failed: {len(state.failed)}"
        )
        
        if state.failed:
            last_failed = state.failed[-1]
            self.log_message(
                f"❌ Failed to match: {last_failed.get('name', 'Unknown')} by {', '.join(last_failed.get('artists', ['Unknown']))}",
                "error"
            )
        
        if state.added:
            last_added = state.added[-1]
            self.log_message(
                f"✓ Added: {last_added.get('name', 'Unknown')}",
                "success"
            )
            
    def run_operation(self, operation_func, operation_name):
        """Run a sync operation in a separate thread"""
        if self.is_running:
            messagebox.showwarning("Operation in Progress", "Please wait for the current operation to complete.")
            return
            
        def run():
            try:
                self.is_running = True
                self.status_text.config(text=operation_name, fg=self.colors["warning"])
                self.progress_bar.start(10)
                self.log_message(f"\n{'='*60}", "info")
                self.log_message(f"🚀 Starting: {operation_name}", "info")
                self.log_message(f"{'='*60}\n", "info")
                
                self.state.reset()
                operation_func(AUTH_SERVER, self.state, self.update_ui)
                
                self.log_message(f"\n{'='*60}", "success")
                self.log_message(f"✅ Completed: {operation_name}", "success")
                self.log_message(f"Total Added: {len(self.state.added)} | Total Failed: {len(self.state.failed)}", "info")
                self.log_message(f"{'='*60}\n", "success")
                
                self.status_text.config(text="Completed", fg=self.colors["success"])
                messagebox.showinfo(
                    "Operation Complete",
                    f"{operation_name} completed!\n\nAdded: {len(self.state.added)}\nFailed: {len(self.state.failed)}"
                )
                
            except Exception as e:
                self.log_message(f"\n{'='*60}", "error")
                self.log_message(f"❌ Error: {str(e)}", "error")
                self.log_message(f"{'='*60}\n", "error")
                self.status_text.config(text="Error", fg=self.colors["error"])
                messagebox.showerror("Error", f"Operation failed:\n{str(e)}")
                
            finally:
                self.is_running = False
                self.progress_bar.stop()
                self.progress_label.config(text="Ready")
                
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        
    def export_spotify(self):
        """Export playlists from Spotify"""
        if not self.check_authentication("spotify"):
            self.prompt_authentication("spotify")
            return
        self.run_operation(export_spotify, "Export from Spotify")
        
    def export_ytmusic(self):
        """Export playlists from YouTube Music"""
        if not self.check_authentication("ytmusic"):
            self.prompt_authentication("ytmusic")
            return
        self.run_operation(export_ytmusic, "Export from YouTube Music")
        
    def import_spotify(self):
        """Import playlists to Spotify"""
        if not self.check_authentication("spotify"):
            self.prompt_authentication("spotify")
            return
        self.run_operation(import_spotify, "Import to Spotify")
        
    def import_ytmusic(self):
        """Import playlists to YouTube Music"""
        if not self.check_authentication("ytmusic"):
            self.prompt_authentication("ytmusic")
            return
        self.run_operation(import_ytmusic, "Import to YouTube Music")
        
    def clear_logs(self):
        """Clear the log window"""
        self.log.delete(1.0, "end")
        self.log_message("📝 Logs cleared", "info")
        
    def open_spotify_auth(self):
        """Open Spotify authentication in browser"""
        url = f"{AUTH_SERVER}/spotify/login"
        webbrowser.open(url)
        self.log_message(f"🔐 Opening Spotify authentication: {url}", "info")
        
    def open_ytmusic_auth(self):
        """Open YouTube Music authentication in browser"""
        url = f"{AUTH_SERVER}/ytmusic/login"
        webbrowser.open(url)
        self.log_message(f"🔐 Opening YouTube Music authentication: {url}", "info")
        
    def show_about(self):
        """Show about dialog"""
        about_text = """MuSync - Music Library Synchronization Tool

Version: 1.0.0

A robust music synchronization tool for transferring 
playlists and liked songs between Spotify and YouTube Music.

Features:
• Export/Import playlists between platforms
• Intelligent track matching with confidence scoring
• Real-time progress tracking
• Automatic OAuth token refresh
• Detailed failure reporting

Built with Python, Flask, and Tkinter
        """
        messagebox.showinfo("About MuSync", about_text)


if __name__ == "__main__":
    app = MuSyncApp()
    app.mainloop()
