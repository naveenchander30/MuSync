import threading
import sys
from pathlib import Path

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

# Allow standalone execution
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.state import SyncState
from sync.spotify_import import import_spotify
from sync.spotify_export import export_spotify
from sync.ytmusic_import import import_ytmusic
from sync.ytmusic_export import export_ytmusic
from config import AUTH_SERVER


class MuSyncApp(tb.Window):
    def __init__(self):
        super().__init__(
            title="MuSync",
            themename="darkly",
            size=(1200, 700),
            resizable=(True, True),
        )

        self.state = SyncState()
        self.current_view = None

        self._build_layout()

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    def _build_layout(self):
        container = tb.Frame(self)
        container.pack(fill=BOTH, expand=True)

        self._create_sidebar(container)

        self.content = tb.Frame(container, padding=20)
        self.content.pack(side=RIGHT, fill=BOTH, expand=True)

        self.views = {
            "dashboard": DashboardView(self),
            "export": ExportView(self),
            "import": ImportView(self),
            "logs": LogsView(self),
            "settings": SettingsView(self),
        }

        for view in self.views.values():
            view.frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_view("dashboard")

    def _create_sidebar(self, parent):
        sidebar = tb.Frame(parent, width=220, padding=10)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)

        tb.Label(
            sidebar,
            text="MuSync",
            font=("Segoe UI", 20, "bold"),
            bootstyle="primary",
        ).pack(pady=(20, 30))

        def nav(text, view):
            return tb.Button(
                sidebar,
                text=text,
                bootstyle="secondary",
                command=lambda: self.show_view(view),
                width=20,
            )

        nav("Dashboard", "dashboard").pack(pady=6)
        nav("Export", "export").pack(pady=6)
        nav("Import", "import").pack(pady=6)
        nav("Logs", "logs").pack(pady=6)
        nav("Settings", "settings").pack(pady=6)

    # --------------------------------------------------
    # View switching
    # --------------------------------------------------

    def show_view(self, name):
        if self.current_view:
            self.current_view.frame.lower()
        self.current_view = self.views[name]
        self.current_view.frame.lift()

    # --------------------------------------------------
    # Sync runner
    # --------------------------------------------------

    def run_task(self, func):
        self.state.reset()
        dashboard = self.views["dashboard"]
        dashboard.set_running(True)
        dashboard.log(f"\n{'='*60}")
        dashboard.log(f"🚀 Starting: {func.__name__.replace('_', ' ').title()}")
        dashboard.log(f"{'='*60}\n")

        def wrapped_task():
            try:
                func(AUTH_SERVER, self.state, self.update_ui)
                self.after(0, self._task_complete, func.__name__)
            except Exception as e:
                self.after(0, self._task_error, str(e))

        threading.Thread(target=wrapped_task, daemon=True).start()
    
    def _task_complete(self, task_name):
        dashboard = self.views["dashboard"]
        dashboard.set_running(False)
        dashboard.log(f"\n{'='*60}")
        dashboard.log(f"✅ Completed: {task_name.replace('_', ' ').title()}")
        dashboard.log(f"📊 Total Added: {len(self.state.added)} | Total Failed: {len(self.state.failed)}")
        dashboard.log(f"{'='*60}\n")
        
        Messagebox.show_info(
            f"Operation completed!\n\n"
            f"✅ Added: {len(self.state.added)}\n"
            f"❌ Failed: {len(self.state.failed)}",
            title="Success"
        )
    
    def _task_error(self, error_msg):
        dashboard = self.views["dashboard"]
        dashboard.set_running(False)
        dashboard.log(f"\n{'='*60}")
        dashboard.log(f"❌ Error: {error_msg}")
        dashboard.log(f"{'='*60}\n")
        
        Messagebox.show_error(
            f"Operation failed:\n\n{error_msg}",
            title="Error"
        )

    def update_ui(self, state):
        self.after(0, self._refresh_ui, state)

    def _refresh_ui(self, state):
        dashboard = self.views["dashboard"]
        dashboard.update_stats(state)
        
        # Log to dashboard
        if state.current_playlist:
            dashboard.log(f"⏳ Processing: {state.current_playlist}")
        
        # Log successes and failures
        if state.added and len(state.added) > 0:
            last = state.added[-1]
            dashboard.log(f"✅ Added: {last.get('name', 'Unknown')}")
            self.views["logs"].log_all(f"✅ Added: {last.get('name', 'Unknown')}")
        
        if state.failed and len(state.failed) > 0:
            last = state.failed[-1]
            dashboard.log(f"❌ Failed: {last.get('name', 'Unknown')} - Low confidence match")
            self.views["logs"].log_all(f"❌ Failed: {last.get('name', 'Unknown')}")

    # --------------------------------------------------
    # Actions
    # --------------------------------------------------

    def check_auth(self, service="spotify"):
        """Check if authenticated with service"""
        import requests
        try:
            url = f"{AUTH_SERVER}/{service}/token"
            resp = requests.get(url, timeout=30)
            return resp.status_code == 200
        except:
            return False

    def prompt_auth(self, service="spotify"):
        """Prompt user to authenticate"""
        import webbrowser
        service_name = "Spotify" if service == "spotify" else "YouTube Music"
        
        result = Messagebox.yesno(
            f"You need to authenticate with {service_name} first.\n\n"
            f"Would you like to open the login page now?",
            title="Authentication Required"
        )
        
        if result == "Yes":
            url = f"{AUTH_SERVER}/{service}/login"
            webbrowser.open(url)
            Messagebox.show_info(
                f"Please complete the {service_name} authentication in your browser, "
                f"then try the operation again.",
                title="Complete Authentication"
            )

    def export_spotify(self):
        if not self.check_auth("spotify"):
            self.prompt_auth("spotify")
            return
        self.run_task(export_spotify)

    def import_spotify(self):
        if not self.check_auth("spotify"):
            self.prompt_auth("spotify")
            return
        self.run_task(import_spotify)

    def export_ytmusic(self):
        if not self.check_auth("ytmusic"):
            self.prompt_auth("ytmusic")
            return
        self.run_task(export_ytmusic)

    def import_ytmusic(self):
        if not self.check_auth("ytmusic"):
            self.prompt_auth("ytmusic")
            return
        self.run_task(import_ytmusic)


# ==================================================
# Views
# ==================================================

class BaseView:
    def __init__(self, app):
        self.app = app
        self.frame = tb.Frame(app.content, padding=10)


class DashboardView(BaseView):
    def __init__(self, app):
        super().__init__(app)

        # Header with gradient-like effect
        header = tb.Frame(self.frame)
        header.pack(fill=X, pady=(0, 20))
        
        tb.Label(
            header,
            text="🎵 MuSync Dashboard",
            font=("Segoe UI", 24, "bold"),
            bootstyle="primary",
        ).pack(anchor=W)
        
        tb.Label(
            header,
            text="Sync your music library seamlessly",
            font=("Segoe UI", 10),
            bootstyle="secondary",
        ).pack(anchor=W)

        # Quick Actions Section
        actions_frame = tb.Labelframe(
            self.frame,
            text="⚡ Quick Actions",
            padding=15,
        )
        actions_frame.pack(fill=X, pady=(0, 20))
        
        actions_grid = tb.Frame(actions_frame)
        actions_grid.pack(fill=X)
        
        # Export buttons
        export_col = tb.Frame(actions_grid)
        export_col.pack(side=LEFT, expand=True, fill=X, padx=5)
        
        tb.Button(
            export_col,
            text="📥 Export Spotify",
            bootstyle="success-outline",
            command=app.export_spotify,
            width=20,
        ).pack(fill=X, pady=5)
        
        tb.Button(
            export_col,
            text="📥 Export YouTube Music",
            bootstyle="danger-outline",
            command=app.export_ytmusic,
            width=20,
        ).pack(fill=X, pady=5)
        
        # Import buttons
        import_col = tb.Frame(actions_grid)
        import_col.pack(side=LEFT, expand=True, fill=X, padx=5)
        
        tb.Button(
            import_col,
            text="📤 Import to Spotify",
            bootstyle="success",
            command=app.import_spotify,
            width=20,
        ).pack(fill=X, pady=5)
        
        tb.Button(
            import_col,
            text="📤 Import to YouTube Music",
            bootstyle="danger",
            command=app.import_ytmusic,
            width=20,
        ).pack(fill=X, pady=5)

        # Stats Cards
        stats_frame = tb.Labelframe(
            self.frame,
            text="📊 Statistics",
            padding=15,
        )
        stats_frame.pack(fill=X, pady=(0, 20))
        
        cards = tb.Frame(stats_frame)
        cards.pack(fill=X)

        self.status = self._card(cards, "⚙️ Status", "Idle", "info", large=False)
        self.added = self._card(cards, "✅ Tracks Added", "0", "success", large=True)
        self.failed = self._card(cards, "❌ Failed", "0", "danger", large=True)
        self.current_playlist = self._card(cards, "📁 Current", "-", "secondary", large=False)

        # Live Logs Section
        logs_frame = tb.Labelframe(
            self.frame,
            text="📝 Activity Log",
            padding=15,
        )
        logs_frame.pack(fill=BOTH, expand=True)
        
        # Progress bar
        self.progress = tb.Progressbar(
            logs_frame,
            mode='indeterminate',
            bootstyle="success-striped",
        )
        self.progress.pack(fill=X, pady=(0, 10))
        
        # Scrolled text for logs
        self.log_text = tb.ScrolledText(
            logs_frame,
            height=15,
            autohide=True,
            wrap="word",
        )
        self.log_text.pack(fill=BOTH, expand=True)

    def _card(self, parent, title, value, style, large=True):
        card = tb.Frame(parent, padding=15, bootstyle=f"{style}")
        card.pack(side=LEFT, expand=True, fill=BOTH, padx=5)

        tb.Label(
            card, 
            text=title, 
            font=("Segoe UI", 9),
            bootstyle="inverse-secondary"
        ).pack()
        
        lbl = tb.Label(
            card,
            text=value,
            font=("Segoe UI", 22 if large else 14, "bold"),
            bootstyle="inverse-" + style,
        )
        lbl.pack()
        return lbl

    def update_stats(self, state):
        self.added.config(text=str(len(state.added)))
        self.failed.config(text=str(len(state.failed)))
        if state.current_playlist:
            self.current_playlist.config(text=state.current_playlist[:25] + "..." if len(state.current_playlist) > 25 else state.current_playlist)

    def set_running(self, running):
        self.status.config(text="🔄 Running" if running else "✓ Idle")
        if running:
            self.progress.start(10)
        else:
            self.progress.stop()
    
    def log(self, message):
        """Add message to dashboard logs"""
        self.log_text.insert(END, message + "\n")
        self.log_text.see(END)


class ExportView(BaseView):
    def __init__(self, app):
        super().__init__(app)

        tb.Label(
            self.frame,
            text="Export",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor=W, pady=(0, 20))

        tb.Button(
            self.frame,
            text="Export Spotify → JSON",
            bootstyle="primary",
            command=app.export_spotify,
            width=30,
        ).pack(pady=10)

        tb.Button(
            self.frame,
            text="Export YTMusic → JSON",
            bootstyle="primary",
            command=app.export_ytmusic,
            width=30,
        ).pack(pady=10)


class ImportView(BaseView):
    def __init__(self, app):
        super().__init__(app)

        tb.Label(
            self.frame,
            text="Import",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor=W, pady=(0, 20))

        tb.Button(
            self.frame,
            text="Import JSON → Spotify",
            bootstyle="success",
            command=app.import_spotify,
            width=30,
        ).pack(pady=10)

        tb.Button(
            self.frame,
            text="Import JSON → YTMusic",
            bootstyle="success",
            command=app.import_ytmusic,
            width=30,
        ).pack(pady=10)


class LogsView(BaseView):
    def __init__(self, app):
        super().__init__(app)

        tb.Label(
            self.frame,
            text="Logs",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor=W, pady=(0, 10))

        self.text = tb.Text(self.frame, height=25)
        self.text.pack(fill=BOTH, expand=True)

    def log_all(self, msg):
        self.text.insert(END, msg + "\n")
        self.text.see(END)


class SettingsView(BaseView):
    def __init__(self, app):
        super().__init__(app)

        tb.Label(
            self.frame,
            text="Settings",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor=W, pady=(0, 10))

        tb.Label(
            self.frame,
            text=f"Auth Server: {AUTH_SERVER}",
            wraplength=500,
        ).pack(anchor=W, pady=10)

        # Authentication section
        auth_frame = tb.Labelframe(
            self.frame,
            text="Authentication",
            padding=15,
        )
        auth_frame.pack(fill=X, pady=20)

        tb.Button(
            auth_frame,
            text="🔐 Login to Spotify",
            bootstyle="success",
            command=self.login_spotify,
            width=25,
        ).pack(pady=5)

        tb.Button(
            auth_frame,
            text="🔐 Login to YouTube Music",
            bootstyle="danger",
            command=self.login_ytmusic,
            width=25,
        ).pack(pady=5)

        tb.Button(
            self.frame,
            text="About",
            bootstyle="secondary",
            command=self.about,
        ).pack(pady=10)

    def login_spotify(self):
        import webbrowser
        url = f"{AUTH_SERVER}/spotify/login"
        webbrowser.open(url)
        Messagebox.show_info(
            "Complete the Spotify authentication in your browser.",
            title="Spotify Login"
        )

    def login_ytmusic(self):
        import webbrowser
        url = f"{AUTH_SERVER}/ytmusic/login"
        webbrowser.open(url)
        Messagebox.show_info(
            "Complete the YouTube Music authentication in your browser.",
            title="YouTube Music Login"
        )

    def about(self):
        Messagebox.show_info(
            "MuSync\n\n"
            "• Cross-platform playlist sync\n"
            "• Automatic OAuth refresh\n"
            "• Intelligent matching\n"
            "• Real-time GUI",
            title="About MuSync",
        )


# --------------------------------------------------

if __name__ == "__main__":
    MuSyncApp().mainloop()
